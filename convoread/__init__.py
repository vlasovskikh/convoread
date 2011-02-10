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

__version__ = '0.1'

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
    'NOTIFY': False,
    'NETWORK_ENCODING': 'UTF-8',
    'LIVE_URL': '/api/live.json',
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


def livestream(conn, login=None, password=None):
    '''Return an iterable over live messages.'''
    headers = {}
    if login is not None and password is not None:
        headers[b'Authorization'] = authheader(login, password)
    cursor = 'null'
    while True:
        params = {
            'cursor': cursor,
        }
        url = '{path}?{params}'.format(
                  path=config['LIVE_URL'],
                  params=urlencode(params))
        debug('GET {0} HTTP/1.1'.format(url))
        conn.request('GET', url, headers=headers)
        r = conn.getresponse()
        if r.status // 100 != 2:
            error('HTTP error {status} {reason}'.format(
                status=r.status,
                reason=r.reason))
            conn.close()
            conn.connect()
            continue
        data = r.read().decode(config['NETWORK_ENCODING'])
        try:
            event = json.loads(data)
        except ValueError:
            error('bad json string: {0}'.format(data))
            continue

        messages = event.get('messages', [])
        if messages:
            cursor = messages[-1].get('_id', 'null')
        for m in messages:
            yield m


def display(message, fd):
    kind = message.get('kind', 'unknown')
    debug('got "{0}" message'.format(kind))
    debug('message in json\n{msg}'.format(
        msg=json.dumps(message, ensure_ascii=False, indent=4)))

    if kind == 'message':
        title = '{time} @{user}'.format(
            time=datetime.now().strftime('%H:%M'),
            user=message.get('user', {}).get('username', '<anonymous>'),)
        body = message.get('message', '<empty>')
        s = '{0}: {1}'.format(title, body)
    else:
        s = None

    if s is not None:
        print(s.encode(ENCODING), file=fd)
        if config['NOTIFY']:
            notify_display(title, body)


def authheader(login, password):
    s = '%s:%s' % (login, password)
    value = base64.b64encode(s.encode(config['NETWORK_ENCODING']))
    return b'Basic ' + value


def getpasswd():
    '''Read config for username and password'''
    rc = netrc()
    login = password = None
    res = rc.authenticators(config['HOSTNAME'])
    if res:
        login, _, password = res
    return login, password


def usage():
    print('''usage: convoread.py [OPTIONS]

options:

  -h --help     show help
  --debug       show debug messages
  --notify      show desktop notifications
'''.encode(ENCODING), file=stderr)


def worker(argv):
    try:
        opts, args = getopt(argv, b'h', [b'help', b'debug', b'notify'])
    except GetoptError, e:
        error(bytes(e).decode(ENCODING, errors='replace'))
        usage()
        sys.exit(1)

    for opt, arg in opts:
        if opt in [b'-h', b'--help']:
            usage()
            sys.exit(0)
        elif opt == b'--debug':
            config['DEBUG'] = True
        elif opt == b'--notify':
            config['NOTIFY'] = True

    with closing(HTTPSConnection(config['HOSTNAME'])) as conn:
        login, password = getpasswd()
        for msg in livestream(conn, login, password):
            try:
                display(msg, stdout)
            except KeyError:
                debug(str(msg))


def main():
    global stdout, stderr
    stdout = os.fdopen(sys.stdout.fileno(), 'wb')
    stderr = os.fdopen(sys.stderr.fileno(), 'wb')
    try:
        worker(sys.argv[1:])
    except KeyboardInterrupt:
        print('interrupted', file=stderr)
        pass

if __name__ == '__main__':
    main()
