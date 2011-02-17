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

from datetime import datetime

from convoread.convore import Convore, NetworkError
from convoread.config import config
from convoread.utils import get_passwd, error, debug, output, wrap_string


class Console(object):
    def __init__(self, convore):
        self.convore = convore
        self.convore.on_live_update(self.handle_live_update)
        self.topic = None


    def handle_live_update(self, message):
        username = message.get('user', {}).get('username', '(unknown)')
        me = self.convore.get_username()
        if message.get('kind') != 'message' or username == me:
            return

        group = self.convore.get_groups().get(message.get('group'), {})
        title = '[{time}] {group}/{topic} <{user}>'.format(
            time=datetime.now().strftime('%H:%M'),
            group=group.get('slug', '(unkonwn)'),
            topic=message.get('topic', {}).get('id', '(unknown)'),
            user=username)
        body = wrap_string(message.get('message', '(empty)'))
        output('{0}\n{1}'.format(title, body), async=True)


    def loop(self):
        output('welcome to convoread! type /help for more info')
        while True:
            data = raw_input(config['PROMPT'])
            self.dispatch(data.decode(config['ENCODING'], 'replace'))


    def dispatch(self, msg):
        badcmd = 'bad command, type /help for more info'
        if not msg:
            return
        if msg.startswith('/'):
            args = msg[1:].split()
            try:
                cmd = args.pop(0)
            except IndexError:
                error(badcmd)
                return
            method = getattr(self, 'cmd_' + cmd, None)
            if method:
                try:
                    method(*args)
                except TypeError:
                    error(badcmd)
                    return
            else:
                error(badcmd)
        else:
            self.sendmsg(msg)


    def cmd_q(self):
        raise EOFError()


    def cmd_t(self, topic=None):
        if topic:
            self.topic = topic
            return
        count = 10
        try:
            groups = self.convore.get_groups()
            topics = self.convore.get_topics(groups)
        except NetworkError, e:
            error(unicode(e))
            return
        recent = sorted(topics.itervalues(),
                        key=lambda x: x.get('date_latest_message'),
                        reverse=True)
        for t in list(recent)[:count]:
            msg = ' {mark} {id:6} {name}'.format(
                mark='*' if t.get('id', '?') == self.topic else ' ',
                id=t.get('id', '?'),
                name=t.get('name', '<unknown>'))
            output(msg)


    def cmd_ls(self, topic=None):
        if not topic:
            if self.topic:
                topic = self.topic
            else:
                error('no topic set, type /help for more info')
                return
        try:
            messages = self.convore.get_topic_messages(topic)
        except NetworkError, e:
            error(unicode(e))
            return
        for message in messages:
            username = message.get('user', {}).get('username', '(unknown)')
            try:
                # TODO: Time is not in the local timezone now
                created = datetime.fromtimestamp(message.get('date_created'))
            except:
                created = datetime.now()
            title = '[{time}] <{user}>'.format(
                time=created.strftime('%H:%M'),
                user=username)
            body = wrap_string(message.get('message', '(empty)'))
            output('{0}\n{1}'.format(title, body))


    def cmd_help(self):
        output('''\
commands:

  /t [num]    list recent topics or set current topic to <num>
  /ls [num]   list recent messages in topic (current or <num>)
  /help       show help on commands
  /q          quit
  <text>      post a new message

keys:

  C-u         clear command line
  C-d         quit
''')


    def sendmsg(self, msg):
        if not self.topic:
            error('no topic set, type /help for more info')
            return
        msg = msg.strip()
        if not msg:
            return
        debug('sending "{0}"...'.format(msg))
        try:
            self.convore.send_message(self.topic, msg)
        except NetworkError, e:
            error(unicode(e))

