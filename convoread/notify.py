# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import os
from tempfile import mkdtemp
from shutil import rmtree
from urllib import urlopen
from hashlib import sha1
from contextlib import closing

try:
    import pynotify
except ImportError:
    pynotify = None

from convoread.utils import error, debug


class Notifier(object):
    def __init__(self):
        if not pynotify:
            return

        self._tmpdir = mkdtemp()
        pynotify.init('convoread')


    def display(self, convore, message):
        if not pynotify:
            return

        kind = message.get('kind')
        user = message.get('user', {})
        username = user.get('username', '<anonymous>')
        img = self.imgpath(user)
        body = ''
        timeout = 5000

        if kind == 'message' and username != convore.username:
            group = convore.get_groups().get(message.get('group'), {})
            title = '!{group} @{user}'.format(
                group=group.get('slug', '<unkonwn>'),
                user=username)
            body = message.get('message', '<empty>')
            timeout = 15000
        # TODO: Presence notifications are too noisy
        #elif kind == 'login':
        #    title = '@{user} logged in'.format(user=username)
        #elif kind == 'logout':
        #    title = '@{user} logged out'.format(user=username)
        else:
            return

        n = pynotify.Notification(title, body, img)
        n.set_timeout(timeout)
        n.show()


    def imgpath(self, user):
        if not self.Image:
            return

        try:
            img = user['img']
        except KeyError:
            return None

        filename = '{hash}.jpg'.format(hash=sha1(img).hexdigest())
        path = os.path.join(self._tmpdir, filename)

        if not os.path.exists(path):
            debug('GET {url} HTTP/1.1'.format(url=img))
            with closing(urlopen(img)) as src:
                blocks = iter(lambda: src.read(4096), b'')
                with closing(open(path, 'wb')) as dst:
                    for block in blocks:
                        dst.write(block)
            img = self.Image.open(path)
            img.thumbnail((64, 64), self.Image.ANTIALIAS)
            img.save(path)

        return 'file://' + path


    @property
    def Image(self):
        if not hasattr(self, '_Image'):
            try:
                from PIL import Image
                self._Image = Image
            except ImportError:
                error('Python Imaging Library is not installed, '
                      'no avatars will be shown')
                self._Image = None
        return self._Image


    def close(self):
        if not pynotify:
            return

        rmtree(self._tmpdir)

