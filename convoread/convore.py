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
from httplib import HTTPSConnection, HTTPException
from urllib import urlencode
import socket
from contextlib import closing
from threading import Thread

from convoread.config import config
from convoread.utils import debug, error, get_passwd, synchronized


class NetworkError(Exception):
    pass


class Convore(object):
    def __init__(self):
        self._connection = Connection()
        self._live = Live()
        self._live.on_update(self._handle_live_update)


    @synchronized
    def get_username(self):
        return self._connection.username


    @synchronized
    def get_groups(self):
        def groupid(g):
            try:
                return int(g.get('id'))
            except ValueError:
                return None
        response = self._connection.request('GET', config['GROUPS_URL'])
        result = dict((groupid(g), g) for g in response.get('groups', []))
        return result


    @synchronized
    def get_topics(self, groups):
        topics = {}
        for group in groups:
            url = config['TOPICS_URL'].format(group)
            gtopics = self._connection.request('GET', url)
            for topic in gtopics.get('topics', []):
                topics[topic['id']] = topic
        return topics


    @synchronized
    def get_topic_messages(self, topic):
        url = config['TOPIC_MESSAGES_URL'].format(topic)
        return self._connection.request('GET', url).get('messages', [])


    @synchronized
    def send_message(self, topic, msg):
        data = msg.encode(config['NETWORK_ENCODING'], 'replace')
        self._connection.request('POST',
                                 config['CREATE_MSG_URL'].format(topic),
                                 params={'message': data})


    @synchronized
    def on_live_update(self, callback):
        self._live.on_update(callback)


    @synchronized
    def close(self):
        self._connection.close()
        self._live.close()


    @synchronized
    def _handle_live_update(self, message):
        pass


class Connection(object):
    def __init__(self):
        # Credentials are stored in .netrc now. If we need different ways of
        # storing them, we will turn them into arguments
        login, password = get_passwd()
        self.username = login
        self.http = HTTPSConnection(config['HOSTNAME'])
        self._headers = {
            b'Authorization': authheader(login, password),
        }


    def request(self, method, url, params={}):
        body = None
        if params:
            if method == 'GET':
                url = '{path}?{params}'.format(path=url,
                                               params=urlencode(params))
            else:
                body = urlencode(params)
        debug('GET {0} HTTP/1.1'.format(url))
        try:
            self.http.connect()
        except socket.gaierror:
            msg = 'cannot get network address for "{host}"'.format(
                    host=self.http.host)
            raise NetworkError(msg)
        try:
            self.http.request(method, url, body, headers=self._headers)
            r = self.http.getresponse()
        except HTTPException, e:
            self.http.close()
            raise NetworkError('HTTP request error: {0}'.format(
                    type(e).__name__))
        except socket.error, e:
            self.http.close()
            raise NetworkError(e.args[1])
        if r.status // 100 != 2:
            msg = 'server error: {status} {reason}'.format(status=r.status,
                                                           reason=r.reason)
            self.http.close()
            raise NetworkError(msg)
        try:
            data = r.read().decode(config['NETWORK_ENCODING'])
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

        with closing(self._connection):
            headers = {}
            while True:
                try:
                    url = config['LIVE_URL']
                    event = self._connection.request('GET', url, headers)
                except NetworkError, e:
                    n = 10
                    error('{msg}, waiting for {n} secs...'.format(
                              msg=unicode(e),
                              n=n))
                    time.sleep(n)
                    continue

                messages = event.get('messages', [])
                if messages:
                    headers['cursor'] = messages[-1].get('_id', 'null')
                # TODO: Handle exceptions in callbacks
                for f in self._callbacks:
                    for m in messages:
                        f(m)


def authheader(login, password):
    s = '%s:%s' % (login, password)
    value = base64.b64encode(s.encode(config['NETWORK_ENCODING']))
    return b'Basic ' + value

