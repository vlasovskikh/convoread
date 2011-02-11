# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

import sys
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


class Notifier(object):
    def __init__(self):
        self._tmpdir = mkdtemp()
        pynotify.init('Convoread')


    def display(self, convore, message):
        if not pynotify:
            return

        kind = message.get('kind')
        user = message.get('user', {})
        username = user.get('username', '<anonymous>')
        img = self.imgpath(user)
        body = ''
        timeout = 5000

        if kind == 'message':
            group = convore.groups.get(message.get('group'), {})
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
        try:
            img = user['img']
        except KeyError:
            return None

        filename = '{hash}.jpg'.format(hash=sha1(img).hexdigest())
        path = os.path.join(self._tmpdir, filename)

        if not os.path.exists(path):
            # TODO: Use debug() to print HTTP GET
            #print('debug: GET {url} HTTP/1.1'.format(url=img), file=sys.stderr)
            with closing(urlopen(img)) as src:
                blocks = iter(lambda: src.read(4096), b'')
                with closing(open(path, 'wb')) as dst:
                    for block in blocks:
                        dst.write(block)
            try:
                from PIL import Image
                img = Image.open(path)
                img.thumbnail((64, 64), Image.ANTIALIAS)
                img.save(path)
            except ImportError, e:
                # TODO: Show "install PIL" warning using error()
                #print('error: {0}'.format(e), file=sys.stderr)
                pass

        return 'file://' + path


    def close(self):
        rmtree(self._tmpdir)

