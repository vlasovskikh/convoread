#!/usr/bin/env python
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

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function

import sys
import os
import traceback
import multiprocessing
import string
from datetime import datetime
from contextlib import closing
from getopt import getopt, GetoptError

from convoread.convore import Convore
from convoread.config import config
from convoread.input import Input
from convoread.utils import (debug, error, get_passwd, stdout, stderr,
                             wrap_string)
from convoread.notify import Notifier

__version__ = '0.4'

try:
    import locale
    ENCODING = locale.getpreferredencoding()
    if not ENCODING or ENCODING == 'mac-roman' or 'ascii' in ENCODING.lower():
        ENCODING = 'UTF-8'
except locale.Error:
    ENCODING = 'UTF-8'
config['ENCODING'] = ENCODING

try:
    import readline
except ImportError:
    print('warning: readline module not available', file=sys.stderr)


def console_display(convore, message, fd):
    if message.get('kind') != 'message':
        return

    group = convore.get_groups().get(message.get('group'), {})
    username = message.get('user', {}).get('username', '(unknown)')
    title = '[{time}] {group}/{topic} <{user}>'.format(
        time=datetime.now().strftime('%H:%M'),
        group=group.get('slug', '(unkonwn)'),
        topic=message.get('topic', {}).get('id', '(unknown)'),
        user=username)
    body = wrap_string(message.get('message', '(empty)'))

    s = '{0}\n{1}\n'.format(title, body)
    print(s.encode(ENCODING, 'relace'), file=fd)


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
    def __init__(self, notify):
        self.notify = notify
        super(Reader, self).__init__()


    def run(self):
        try:
            login, password = get_passwd()
            with closing(Convore(login, password)) as c:
                with closing(Notifier()) as notifier:
                    for msg in c.get_livestream():
                        debug('got "{0}" message'.format(msg.get('kind', '<unknown>')))

                        console_display(c, msg, stdout)

                        if self.notify:
                            notifier.display(c, msg)
        except EOFError:
            pass


def main():
    global stdout, stderr
    stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
    stderr = os.fdopen(sys.stderr.fileno(), 'wb', 0)

    try:
        opts, args = getopt(sys.argv[1:], b'h', [b'help', b'debug', b'notify'])
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

    reader = Reader(notify=notify)
    try:
        reader.start()
        input = Input()
        print('welcome to convoread! '
              'type /help for more info'.encode(ENCODING),
              file=stderr)
        while True:
            try:
                input.dispatch(raw_input('> '))
            except KeyboardInterrupt:
                pass
    except EOFError:
        print('quit', file=stderr)
    finally:
        reader.terminate()


if __name__ == '__main__':
    main()

