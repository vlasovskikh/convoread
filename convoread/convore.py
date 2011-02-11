#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function

import base64
import json
from httplib import HTTPSConnection
from urllib import urlencode

from config import config
from utils import debug, error


class JSONValueError(Exception):
    pass


class HTTPBadStatusError(Exception):
    pass


class Convore(object):
    def __init__(self, login=None, password=None):
        self._connection = HTTPSConnection(config['HOSTNAME'])
        self._headers = {}
        if login is not None or password is not None:
            self._headers[b'Authorization'] = authheader(login, password)
        self.groups = self.get_groups()
        self.topics = self.get_topics(self.groups)


    def get_groups(self):
        def groupid(g):
            try:
                return int(g.get('id'))
            except ValueError:
                return None
        res = self._request('GET', config['GROUPS_URL'])
        return dict((groupid(g), g) for g in res.get('groups', []))


    def get_topics(self, groups):
        topics = {}
        for group in groups:
            gtopics = self._request('GET', config['TOPICS_URL'].format(group))
            for topic in gtopics.get('topics', []):
                topics[topic['id']] = topic
        return topics
    

    def send_message(self, topic, msg):
        try:
            res = self._request('POST',
                    config['CREATE_MSG_URL'].format(topic),
                    params={'message': msg})
        except HTTPBadStatusError:
            print('Error')


    def get_livestream(self):
        '''Return an iterable over live messages.'''
        headers = {}
        while True:
            try:
                event = self._request('GET',
                                      config['LIVE_URL'],
                                      headers)
            except JSONValueError, e:
                error(unicode(e))
                continue
            except HTTPBadStatusError, e:
                error(unicode(e))
                continue

            messages = event.get('messages', [])
            if messages:
                headers['cursor'] = messages[-1].get('_id', 'null')
            for m in messages:
                yield m


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
        self._connection.connect()
        self._connection.request(method, url, body, headers=self._headers)
        r = self._connection.getresponse()
        if r.status // 100 != 2:
            msg = 'HTTP error: {status} {reason}'.format(status=r.status,
                                                         reason=r.reason)
            self._connection.close()
            raise HTTPBadStatusError(msg)
        try:
            data = r.read().decode(config['NETWORK_ENCODING'])
            res = json.loads(data)
            debug('response in json\n{msg}'.format(
                msg=json.dumps(res, ensure_ascii=False, indent=4)))
            return res
        except ValueError:
            raise JSONValueError('bad json string: {0}'.format(data))


def authheader(login, password):
    s = '%s:%s' % (login, password)
    value = base64.b64encode(s.encode(config['NETWORK_ENCODING']))
    return b'Basic ' + value


