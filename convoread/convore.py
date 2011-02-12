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

from convoread.config import config
from convoread.utils import debug, error


class NetworkError(Exception):
    pass


class Convore(object):
    def __init__(self, login=None, password=None):
        self.username = login
        self._connection = HTTPSConnection(config['HOSTNAME'])
        self._headers = {}
        self._groups = None
        self._topics = None
        if login is not None or password is not None:
            self._headers[b'Authorization'] = authheader(login, password)


    def get_groups(self):
        if self._groups:
            return self._groups
        def groupid(g):
            try:
                return int(g.get('id'))
            except ValueError:
                return None
        response = self._request('GET', config['GROUPS_URL'])
        result = dict((groupid(g), g) for g in response.get('groups', []))
        self._groups = result
        return result


    def get_topics(self, groups):
        if self._topics:
            return self._topics
        topics = {}
        for group in groups:
            gtopics = self._request('GET', config['TOPICS_URL'].format(group))
            for topic in gtopics.get('topics', []):
                topics[topic['id']] = topic
        self._topics = topics
        return topics


    def send_message(self, topic, msg):
        self._request('POST',
                      config['CREATE_MSG_URL'].format(topic),
                      params={'message': msg})


    def get_livestream(self):
        '''Return an iterable over live messages.'''
        headers = {}
        while True:
            try:
                try:
                    event = self._request('GET',
                                          config['LIVE_URL'],
                                          headers)
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
                for m in messages:
                    yield m
            except KeyboardInterrupt:
                pass


    def close(self):
        self._connection.close()


    def _request(self, method, url, params={}):
        body = None
        if params:
            if method == 'GET':
                url = '{path}?{params}'.format(path=url,
                                           params=urlencode(params))
            else:
                body = urlencode(params)
        debug('GET {0} HTTP/1.1'.format(url))
        try:
            self._connection.connect()
        except socket.gaierror:
            msg = 'cannot get network address for "{host}"'.format(
                    host=self._connection.host)
            raise NetworkError(msg)
        try:
            self._connection.request(method, url, body, headers=self._headers)
            r = self._connection.getresponse()
        except HTTPException, e:
            self._connection.close()
            raise NetworkError('HTTP request error: {0}'.format(
                    type(e).__name__))
        except socket.error, e:
            self._connection.close()
            raise NetworkError(e.args[1])
        if r.status // 100 != 2:
            msg = 'server error: {status} {reason}'.format(status=r.status,
                                                           reason=r.reason)
            self._connection.close()
            raise NetworkError(msg)
        try:
            data = r.read().decode(config['NETWORK_ENCODING'])
            res = json.loads(data)
            debug('response in json\n{msg}'.format(
                msg=json.dumps(res, ensure_ascii=False, indent=4)))
            return res
        except ValueError:
            raise NetworkError('bad server response: {0}'.format(data))


def authheader(login, password):
    s = '%s:%s' % (login, password)
    value = base64.b64encode(s.encode(config['NETWORK_ENCODING']))
    return b'Basic ' + value

