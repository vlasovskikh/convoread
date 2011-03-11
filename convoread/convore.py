# -*- coding: utf-8 -*-

# Copyright (C) 2011 The Convoread Authors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import unicode_literals, print_function

import base64
import json
import time
from httplib import (HTTPSConnection, HTTPException, CannotSendRequest,
                     BadStatusLine)
from urllib import urlencode
import socket
from contextlib import closing
from threading import Thread

from convoread.utils import debug, error, get_passwd, synchronized


NETWORK_ENCODING = 'UTF-8'


class NetworkError(Exception):
    pass


class Convore(object):
    def __init__(self):
        self._connection = Connection()
        self._live = Live()
        self._live.on_update(self._handle_live_update)
        self._topics = {}
        self._groups = {}


    @synchronized
    def get_username(self):
        return self._connection.username


    @synchronized
    def get_groups(self, force=False):
        if self._groups and not force:
            return self._groups
        url = '/api/groups.json'
        response = self._connection.request('GET', url)
        for group in response.get('groups', []):
            self._groups[group.get('id')] = group
        return self._groups


    @synchronized
    def get_topics(self, force=False):
        if self._topics and not force:
            return self._topics
        for group in self.get_groups():
            self._topics.update(self.get_group_topics(group))
        return self._topics


    @synchronized
    def get_group_topics(self, group_id):
        result = {}
        url = '/api/groups/{0}/topics.json'.format(group_id)
        response = self._connection.request('GET', url)
        for topic in response.get('topics', []):
            topic['group'] = group_id
            result[topic.get('id')] = topic
        return result


    @synchronized
    def get_topic_messages(self, topic_id):
        url = '/api/topics/{0}/messages.json'.format(topic_id)
        messages = self._connection.request('GET', url).get('messages', [])

        topic = self.get_topics().get(topic_id, {})
        unread = topic.get('unread', 0)
        group = self.get_groups().get(topic.get('group'), {})
        group['unread'] = max(group.get('unread', 0) - unread, 0)
        topic['unread'] = 0

        return messages


    @synchronized
    def send_message(self, topic, msg):
        url = '/api/topics/{0}/messages/create.json'.format(topic)
        data = msg.encode(NETWORK_ENCODING, 'replace')
        self._connection.request('POST', url, params={'message': data})


    @synchronized
    def on_live_update(self, callback):
        self._live.on_update(callback)


    @synchronized
    def close(self):
        self._connection.close()
        self._live.close()


    @synchronized
    def mark_all_read(self):
        url = '/api/account/mark_read.json'
        self._connection.request('POST', url)
        for topic in self.get_topics().values():
            topic['unread'] = 0


    @synchronized
    def mark_group_read(self, group_id):
        url = '/api/groups/{0}/mark_read.json'.format(group_id)
        self._connection.request('POST', url)
        for topic in self.get_topics().values():
            if topic.get('group') == group_id:
                topic['unread'] = 0


    @synchronized
    def _handle_live_update(self, message):
        if message.get('kind') != 'message':
            return

        id = message.get('topic', {}).get('id')
        group_id = message.get('group')
        topics = self.get_topics()
        ts = message.get('_ts')

        if id in topics:
            topics[id]['date_latest_message'] = ts
        else:
            group_topics = self.get_group_topics(group_id)
            topics[id] = group_topics.get(id, {})
        groups = self.get_groups()
        if group_id not in groups:
            groups = self.get_groups(force=True)
        groups[group_id]['date_latest_message'] = ts


class Connection(object):
    def __init__(self):
        # Credentials are stored in .netrc now. If we need different ways of
        # storing them, we will turn them into arguments
        login, password = get_passwd()
        self.username = login
        self.http = HTTPSConnection('convore.com')
        self._headers = {
            b'Authorization': authheader(login, password),
        }


    def request(self, method, url, params=None):
        body = None
        if params:
            if method == 'GET':
                url = '{path}?{params}'.format(path=url,
                                               params=urlencode(params))
            else:
                body = urlencode(params)
        debug('GET {0} HTTP/1.1'.format(url))

        def _request():
            self.http.request(method, url, body, headers=self._headers)
            return self.http.getresponse()

        try:
            try:
                r = _request()
            except (CannotSendRequest, BadStatusLine), e:
                debug('exception {0}, reconnecting...'.format(e))
                self.http.close()
                self.http.connect()
                r = _request()
        except HTTPException, e:
            self.http.close()
            raise NetworkError('HTTP request error: {0}'.format(
                    type(e).__name__))
        except socket.gaierror:
            msg = 'cannot get network address for "{host}"'.format(
                    host=self.http.host)
            raise NetworkError(msg)
        except socket.error, e:
            self.http.close()
            raise NetworkError(e.args[1])

        status_msg = '{status} {reason}'.format(status=r.status,
                                                reason=r.reason)
        debug('HTTP/1.1 {0}'.format(status_msg))
        if r.status // 100 != 2:
            self.http.close()
            raise NetworkError('server error: {0}'.format(status_msg))

        try:
            data = r.read().decode(NETWORK_ENCODING)
            res = json.loads(data)
            debug('response in JSON\n{msg}'.format(
                msg=json.dumps(res, ensure_ascii=False, indent=4)))
            return res
        except ValueError:
            raise NetworkError('bad server response: {0}'.format(data))


    def close(self):
        self.http.close()


class Live(Thread):
    def __init__(self):
        self._connection = Connection()
        self._callbacks = []

        Thread.__init__(self)
        self.daemon = True
        self.start()


    def on_update(self, callback):
        self._callbacks.append(callback)


    def close(self):
        pass


    def run(self):
        # XXX: Wait for the command line to initialize
        time.sleep(1.0)

        url = '/api/live.json'
        headers = {}
        timeout = 10

        with closing(self._connection):
            while True:
                try:
                    event = self._connection.request('GET', url, headers)
                except NetworkError, e:
                    error('{msg}, waiting for {n} secs...'.format(
                              msg=unicode(e),
                              n=timeout))
                    time.sleep(timeout)
                    continue

                messages = event.get('messages', [])
                if messages:
                    headers['cursor'] = messages[-1].get('_id', 'null')
                for f in self._callbacks:
                    try:
                        for m in messages:
                            f(m)
                    except Exception, e:
                        error(unicode(e), exc=e)


def authheader(login, password):
    s = '%s:%s' % (login, password)
    value = base64.b64encode(s.encode(NETWORK_ENCODING))
    return b'Basic ' + value

