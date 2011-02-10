#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function

from config import config


stdout = None
stderr = None


def debug(msg):
    if config['DEBUG']:
        print('debug: {0}'.format(msg).encode(config['ENCODING']), file=stderr)


def error(msg, exc=False):
    print('error: {0}'.format(msg).encode(ENCODING), file=stderr)
    if exc:
        print(b'Traceback:', file=stderr)
        for line in traceback.format_exc().splitlines():
            print(line.encode(config['ENCODING']), file=stderr)



