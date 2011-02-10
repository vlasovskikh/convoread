#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function

import sys
import os
import base64
import json
import traceback
from contextlib import closing
from datetime import datetime
from netrc import netrc
from httplib import HTTPSConnection
from urllib import urlencode
from getopt import getopt, GetoptError

from notify import notify_display

__version__ = '0.2'

try:
    import locale
    ENCODING = locale.getpreferredencoding()
    if not ENCODING or ENCODING == 'mac-roman' or 'ascii' in ENCODING.lower():
        ENCODING = 'UTF-8'
except locale.Error:
    ENCODING = 'UTF-8'


config = {
    'HOSTNAME': 'convore.com',
    'DEBUG': False,
    'NETWORK_ENCODING': 'UTF-8',
    'LIVE_URL': '/api/live.json',
    'GROUPS_URL': '/api/groups.json',
}

stdout = None
stderr = None


def debug(msg):
    if config['DEBUG']:
        print('debug: {0}'.format(msg).encode(ENCODING), file=stderr)


def error(msg, exc=False):
    print('error: {0}'.format(msg).encode(ENCODING), file=stderr)
    if exc:
        print(b'Traceback:', file=stderr)
        for line in traceback.format_exc().splitlines():
            print(line.encode(ENCODING), file=stderr)


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


    def get_groups(self):
        def groupid(g):
            try:
                return int(g.get('id'))
            except ValueError:
                return None
        res = self._request('GET', config['GROUPS_URL'])
        return dict((groupid(g), g) for g in res.get('groups', []))


    def get_livestream(self):
        '''Return an iterable over live messages.'''
        cursor = 'null'
        while True:
            try:
                event = self._request('GET',
                                      config['LIVE_URL'],
                                      {'cursor': cursor})
            except JSONValueError, e:
                error(unicode(e))
                continue
            except HTTPBadStatusError, e:
                error(unicode(e))
                continue

            messages = event.get('messages', [])
            if messages:
                cursor = messages[-1].get('_id', 'null')
            for m in messages:
                yield m


    def close(self):
        self._connection.close()


    def _request(self, method, url, params={}):
        if params:
            url = '{path}?{params}'.format(path=url,
                                           params=urlencode(params))
        debug('GET {0} HTTP/1.1'.format(url))
        self._connection.request(method, url, headers=self._headers)
        r = self._connection.getresponse()
        if r.status // 100 != 2:
            msg = 'HTTP error: {status} {reason}'.format(status=r.status,
                                                         reason=r.reason)
            self._connection.close()
            self._connection.connect()
            raise HTTPBadStatusError(msg)
        try:
            data = r.read().decode(config['NETWORK_ENCODING'])
            res = json.loads(data)
            debug('response in json\n{msg}'.format(
                msg=json.dumps(res, ensure_ascii=False, indent=4)))
            return res
        except ValueError:
            raise JSONValueError('bad json string: {0}'.format(data))


def console_display(convore, message, fd):
    if message.get('kind') != 'message':
        return

    group = convore.groups.get(message.get('group'), {})
    title = '{time} !{group} @{user}'.format(
        time=datetime.now().strftime('%H:%M'),
        group=group.get('slug', '<unkonwn>'),
        user=message.get('user', {}).get('username', '<anonymous>'),)
    body = message.get('message', '<empty>')
    s = '{0}: {1}'.format(title, body)
    print(s.encode(ENCODING), file=fd)


def authheader(login, password):
    s = '%s:%s' % (login, password)
    value = base64.b64encode(s.encode(config['NETWORK_ENCODING']))
    return b'Basic ' + value


def get_passwd():
    '''Read config for username and password'''
    try:
        rc = netrc(os.path.expanduser('~/.netrc'))
    except IOError:
        print("Please create .netrc in your home dir,"
              " can't work without credentials")
        sys.exit(1)
    login = password = None
    res = rc.authenticators(config['HOSTNAME'])
    if res:
        login, _, password = [s and s.strip() for s in res]
    return login, password


def usage():
    msg = '''usage: convoread [OPTIONS]

convoread (version {version})

options:

  -h --help     show help
  --debug       show debug messages
  --notify      show desktop notifications
'''.format(version=__version__)
    print(msg.encode(ENCODING), file=stderr)


def worker(argv):
    try:
        opts, args = getopt(argv, b'h', [b'help', b'debug', b'notify'])
    except GetoptError, e:
        error(bytes(e).decode(ENCODING, errors='replace'))
        usage()
        sys.exit(1)

    notify = False

    for opt, arg in opts:
        if opt in [b'-h', b'--help']:
            usage()
            sys.exit(0)
        elif opt == b'--debug':
            config['DEBUG'] = True
        elif opt == b'--notify':
            notify = True

    login, password = get_passwd()

    with closing(Convore(login, password)) as c:
        for msg in c.get_livestream():
            debug('got "{0}" message'.format(msg.get('kind', '<unknown>')))

            console_display(c, msg, stdout)

            if notify:
                notify_display(c, msg)


def main():
    global stdout, stderr
    stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
    stderr = os.fdopen(sys.stderr.fileno(), 'wb', 0)
    try:
        worker(sys.argv[1:])
    except KeyboardInterrupt:
        print('interrupted', file=stderr)
        pass

if __name__ == '__main__':
    main()

