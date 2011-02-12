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
import os.path
import traceback
from netrc import netrc

from convoread.config import config


stdout = None
stderr = None


def debug(msg):
    if config['DEBUG']:
        print('debug: {0}'.format(msg).encode(config['ENCODING'], 'replace'),
              file=stderr)


def error(msg, exc=False):
    print('error: {0}'.format(msg).encode(config['ENCODING'], 'replace'),
          file=stderr)
    if exc:
        print(b'Traceback:', file=stderr)
        for line in traceback.format_exc().splitlines():
            print(line.encode(config['ENCODING'], 'replace'), file=stderr)


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
        login, password = res[0].strip(), res[2].strip()
    return login, password

