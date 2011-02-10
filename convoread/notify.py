# -*- coding: utf-8 -*-

from datetime import datetime

initialized = False

try:
    import pynotify
    if pynotify.init("Convoread"):
        initialized = True
except ImportError:
    pass


def notify_display(convore, message):
    if not initialized:
        return
    if message.get('kind') != 'message':
        return

    group = convore.groups.get(message.get('group'), {})
    title = '{time} !{group} @{user}'.format(
        time=datetime.now().strftime('%H:%M'),
        group=group.get('slug', '<unkonwn>'),
        user=message.get('user', {}).get('username', '<anonymous>'),)
    body = message.get('message', '<empty>')

    n = pynotify.Notification(title, body)
    n.set_timeout(15000)
    n.show()

