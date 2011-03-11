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

from __future__ import unicode_literals, print_function

import sys
import os
import traceback
import textwrap
from netrc import netrc
from threading import RLock, current_thread
from functools import wraps

from convoread.config import config

try:
    import readline
except ImportError:
    print('readline module not available', file=sys.stderr)
    readline = None


stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
stderr = os.fdopen(sys.stderr.fileno(), 'wb', 0)


def debug(msg):
    if not config['DEBUG']:
        return
    thread = current_thread()
    async = thread.name != 'MainThread'
    _print('debug: {0}'.format(msg), stderr, async)


def error(msg, exc=False):
    thread = current_thread()
    async = thread.name != 'MainThread'
    _print('error: {0}'.format(msg), stderr, async)
    if exc:
        _print('\n{0}'.format(traceback.format_exc()), stderr, async)


def output(msg, fd=stdout, async=False):
    _print(msg, fd, async)


def _print(msg, fd, async):
    data = msg.encode(config['ENCODING'], 'replace')
    if async and fd.isatty() and readline:
        prompt = config['PROMPT']
        buf = readline.get_line_buffer()
        clear = b'\r' + b' ' * (len(buf) + len(prompt)) + b'\r'
        fd.write(clear)
        fd.write(data)
        fd.write(b'\n')
        fd.write(prompt)
        fd.write(buf)
        fd.flush()
    else:
        fd.write(data)
        fd.write(b'\n')
        fd.flush()


def get_passwd():
    try:
        rc = netrc(os.path.expanduser('~/.netrc'))
    except IOError:
        print("Please create .netrc in your home dir,"
              " can't work without credentials")
        sys.exit(1)
    login = password = None
    res = rc.authenticators('convore.com')
    if res:
        login, password = res[0].strip(), res[2].strip()
    return login, password


def wrap_string(s, indent=4, width=75):
    return '\n'.join((' ' * indent) + line for line in textwrap.wrap(s, width))


def synchronized(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        try:
            lock = self._lock
        except AttributeError:
            lock = self._lock = RLock()
        with lock:
            return f(self, *args, **kwargs)
    return wrapper

