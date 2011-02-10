#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function
import os.path
from netrc import netrc
from config import config

stdout = None
stderr = None


def debug(msg):
    if config['DEBUG']:
        print('debug: {0}'.format(msg).encode(config['ENCODING']), file=stderr)


def error(msg, exc=False):
    print('error: {0}'.format(msg).encode(config['ENCODING']), file=stderr)
    if exc:
        print(b'Traceback:', file=stderr)
        for line in traceback.format_exc().splitlines():
            print(line.encode(config['ENCODING']), file=stderr)


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



