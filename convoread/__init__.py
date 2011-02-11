#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function

import sys
import os
import traceback
import multiprocessing
import string
from contextlib import closing
from datetime import datetime
from getopt import getopt, GetoptError

from convoread.convore import Convore, JSONValueError, HTTPBadStatusError
from convoread.config import config
from convoread.input import Input, InputExit, send_message
from convoread.utils import debug, error, get_passwd, stdout, stderr
from convoread.notify import Notifier

__version__ = '0.3'

try:
    import locale
    ENCODING = locale.getpreferredencoding()
    if not ENCODING or ENCODING == 'mac-roman' or 'ascii' in ENCODING.lower():
        ENCODING = 'UTF-8'
except locale.Error:
    ENCODING = 'UTF-8'
config['ENCODING'] = ENCODING

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


def usage():
    msg = '''usage: convoread [OPTIONS]

convoread (version {version})

options:

  -h --help     show help
  --debug       show debug messages
  --notify      show desktop notifications
'''.format(version=__version__)
    print(msg.encode(ENCODING), file=stderr)


class Reader(multiprocessing.Process):
    def __init__(self, argv):
        self.argv = argv
        self.do_read = True
        super(Reader, self).__init__()

    def run(self):
        try:
            opts, args = getopt(self.argv, b'h', [b'help', b'debug', b'notify'])
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
            with closing(Notifier()) as notifier:
                for msg in c.get_livestream():
                    debug('got "{0}" message'.format(msg.get('kind', '<unknown>')))

                    console_display(c, msg, stdout)

                    if notify:
                        notifier.display(c, msg)


def main():
    global stdout, stderr
    stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
    stderr = os.fdopen(sys.stderr.fileno(), 'wb', 0)
    try:
        reader = Reader(sys.argv[1:])
        reader.start()
        input = Input()
        while True:
            input.dispatch(raw_input('>>> '))
    except (KeyboardInterrupt, InputExit, EOFError):
        print('interrupted', file=stderr)
    finally:
        reader.do_read = False

if __name__ == '__main__':
    main()

