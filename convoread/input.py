#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function
import blinker

import convore
import utils


class InputExit(Exception):
    pass


send_message = blinker.signal('Send Message')


class Input(object):
    def __init__(self):
        self.convore = convore.Convore(*utils.get_passwd())
        self.topic = self.convore.topics.keys()[0]

    def dispatch(self, msg):
        if not msg:
            return
        if msg.startswith('/'):
            args = msg[1:].split()
            cmd = args.pop(0)
            method = getattr(self, 'cmd_' + cmd, None)
            if method:
                method(*args)
            else:
                print('Wrong command')
        else:
            self.sendmsg(msg)

    def cmd_exit(self):
        raise InputExit()

    def cmd_lt(self):
        for topic in self.convore.topics.itervalues():
            print(topic['id'], topic['name'])

    def cmd_st(self, topic):
        self.topic = topic

    def sendmsg(self, msg):
        print('<<<', msg)
        self.convore.send_message(self.topic, msg)
        
