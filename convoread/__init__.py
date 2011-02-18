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
import string
from datetime import datetime
from contextlib import closing
from getopt import getopt, GetoptError

try:
    import readline
except ImportError:
    pass

from convoread.convore import Convore
from convoread.config import config
from convoread.console import Console
from convoread.notify import Notifier

__version__ = b'0.5'

try:
    import locale
    ENCODING = locale.getpreferredencoding()
    if not ENCODING or ENCODING == 'mac-roman' or 'ascii' in ENCODING.lower():
        ENCODING = 'UTF-8'
except locale.Error:
    ENCODING = 'UTF-8'
config['ENCODING'] = ENCODING


def usage():
    msg = '''usage: convoread [OPTIONS]

convoread (version {version})

options:

  -h --help     show help
  --debug       show debug messages
  --notify      show desktop notifications
'''.format(version=__version__)
    print(msg.encode(ENCODING), file=sys.stderr)


def main():
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

    with closing(Convore()) as convore:
        console = Console(convore)
        if notify:
            notifier = Notifier(convore)
        try:
            console.loop()
        except (EOFError, KeyboardInterrupt):
            print('quit', file=sys.stderr)


if __name__ == '__main__':
    main()

