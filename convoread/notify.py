#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''convoread - a tool for using convore.com via CLI'''

initialized = False

try:
    import pynotify
    if pynotify.init("Convoread"):
        initialized = True
except ImportError:
    pass


def notify_display(title, body):
    if not initialized:
        return
    n = pynotify.Notification(title, body)
    n.set_timeout(15000)
    n.show()
