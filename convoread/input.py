#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

from __future__ import unicode_literals, print_function
import blinker


class InputExit(Exception):
    pass


send_message = blinker.signal('Send Message')


class Input(object):

    def dispatch(self, msg):
        if not msg:
            return
        if msg.startswith('/'):
            self.control(msg[1:])
        else:
            self.sendmsg(msg)

    def control(self, cmd):
        if cmd == 'exit':
            raise InputExit()

    def sendmsg(self, msg):
        print('<<<', msg)
        send_message.send(msg)
        
