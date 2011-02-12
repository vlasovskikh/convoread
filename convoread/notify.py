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
            title = '@{user} in {group}/{topic}'.format(
                group=group.get('slug', '<unkonwn>'),
                topic=message.get('topic', {}).get('id', '(unknown)'),
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

