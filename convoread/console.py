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

from convoread.convore import NetworkError
from convoread.config import config
from convoread.utils import error, debug, output, wrap_string


class Console(object):
    def __init__(self, convore):
        self.convore = convore
        self.convore.on_live_update(self.handle_live_update)
        self.topic = None
        self.output_topic = None


    def handle_live_update(self, message):
        username = message.get('user', {}).get('username', '(unknown)')
        me = self.convore.get_username()
        if message.get('kind') != 'message' or username == me:
            return

        topic = message.get('topic', {})
        self.set_output_topic(topic.get('id'), async=True)

        output(_format_message(message), async=True)


    def loop(self):
        output('welcome to convoread! type /help for more info')
        while True:
            try:
                data = raw_input(config['PROMPT'])
                self.dispatch(data.decode(config['ENCODING'], 'replace'))
            except EOFError:
                raise
            except Exception, e:
                error(unicode(e), exc=e)


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


    def cmd_ts(self, group_slug=None):
        def latest_message(x):
            return x.get('date_latest_message')

        try:
            all_topics = list(self.convore.get_topics().values())
            groups = list(self.convore.get_groups().values())
        except NetworkError, e:
            error(unicode(e))
            return

        if group_slug:
            groups = [g for g in groups
                        if g.get('slug') == group_slug]
            if not groups:
                error('group "{0}" not found'.format(group_slug))
                return

        groups = sorted(groups, key=latest_message, reverse=True)

        for group in groups:
            output('{name}:'.format(
                name=group.get('slug', '(unknown)')))
            topics = [t for t in all_topics
                        if t.get('group') == group.get('id')]
            topics = sorted(topics, key=latest_message, reverse=True)
            for topic in topics:
                unread = topic.get('unread', 0)
                if not group_slug and unread == 0:
                    continue
                msg = '  {mark} {id:6} {new:2} {name}'.format(
                    mark='*' if topic.get('id') == self.topic else ' ',
                    id=topic.get('id', '?'),
                    new=unread if unread > 0 else '',
                    name=topic.get('name', '(unknown)'))
                output(msg)


    def cmd_t(self, topic_id=None):
        count = 10
        if topic_id:
            self.topic = topic_id
        else:
            if self.topic:
                topic_id = self.topic
            else:
                error('no topic set, type /help for more info')
                return
        try:
            messages = self.convore.get_topic_messages(topic_id)
        except NetworkError, e:
            error(unicode(e))
            return
        self.output_topic = None
        self.set_output_topic(topic_id)
        for message in messages[-count:]:
            output(_format_message(message))


    def cmd_m(self, group_slug=None):
        try:
            if group_slug:
                groups = [g for g in self.convore.get_groups().values()
                            if g.get('slug') == group_slug]
                if not groups:
                    error('group "{0}" not found'.format(group_slug))
                    return
                group = groups[0]
                self.convore.mark_group_read(group.get('id'))
            else:
                self.convore.mark_all_read()
        except NetworkError, e:
            error(unicode(e))


    def cmd_help(self):
        output('''\
commands:

  /ts [name]  list unread topics or topics in group <name>
  /t [num]    set the posting topic to <num> and list recent messages
  /m [name]   mark messages as read (all or in group <name>)
  /help       show help on commands
  /q          quit
  <text>      post a new message to the selected topic

keys:

  C-u         clear the command line
  C-d         quit
''')


    def set_output_topic(self, topic_id, async=False):
        if topic_id == self.output_topic:
            return
        self.output_topic = topic_id

        topic = self.convore.get_topics().get(topic_id, {})
        group = self.convore.get_groups().get(topic.get('group'), {})

        output('\n*** topic {group}/{id}: {name}'.format(
                    group=group.get('slug', '(unkonwn)'),
                    id=topic_id,
                    name=topic.get('name', '(unknown)')),
               async=async)


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


def _format_message(msg):
    username = msg.get('user', {}).get('username', '(unknown)')
    try:
        created = datetime.fromtimestamp(msg['_ts'])
    except (KeyError, TypeError):
        created = datetime.fromtimestamp(msg['date_created'])
    body = '<{user}> {msg}'.format(user=username,
                                   msg=msg.get('message', '(empty)'))
    return '{time} {body}'.format(
            time=created.strftime('%H:%M'),
            body=wrap_string(body, indent=6).lstrip())

