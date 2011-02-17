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
import subprocess

from convoread.config import config
from convoread.utils import error, debug


class Notifier(object):
    def __init__(self, convore):
        self.convore = convore
        self.convore.on_live_update(self.handle_live_update)
        if os.path.exists(config['NOTIFY_SEND']):
            self.enabled = True
        else:
            error('desktop notifications are disabled: '
                  '"{0}" not found'.format(config['NOTIFY_SEND']))
            self.enabled = False
        self._tmpdir = mkdtemp()


    def handle_live_update(self, message):
        if not self.enabled:
            return

        kind = message.get('kind')
        user = message.get('user', {})
        username = user.get('username', '<anonymous>')

        if kind != 'message' or username == self.convore.get_username():
            return

        img = self.imgpath(user)
        group = self.convore.get_groups().get(message.get('group'), {})
        timeout = 15000
        title = '@{user} in {group}'.format(
            group=group.get('slug', '<unkonwn>'),
            user=username)
        body = '{msg} <a href="https://convore.com{url}">#</a>'.format(
                msg=message.get('message', '<empty>'),
                url=message.get('topic', {}).get('url', '/'))

        cmd = [config['NOTIFY_SEND'], '-t', str(timeout), title, body]
        if img:
            cmd.extend(['-i', img])
        subprocess.call(cmd)


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

        return path


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
        rmtree(self._tmpdir)

