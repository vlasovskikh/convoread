# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

from convoread.convore import Convore, NetworkError
from convoread.config import config
from convoread.utils import get_passwd, error, debug, stdout

class Input(object):
    def __init__(self):
        login, password = get_passwd()
        self.convore = Convore(login, password)
        self.topic = None


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
        groups = self.convore.get_groups()
        topics = self.convore.get_topics(groups)
        recent = sorted(topics.itervalues(),
                        key=lambda x: x.get('date_latest_message'),
                        reverse=True)
        for t in list(recent)[:count]:
            msg = ' {mark} {id:6} {name}'.format(
                mark='*' if t.get('id', '?') == self.topic else ' ',
                id=t.get('id', '?'),
                name=t.get('name', '<unknown>'))
            print(msg.encode(config['ENCODING']), file=stdout)


    def cmd_help(self):
        print('''\
commands:

  /t [num]    list recent topics or switch to topic <num>
  /q          quit convoread
  /help       show help on commands''', file=stdout)


    def sendmsg(self, msg):
        if not self.topic:
            error('no topic set, type /help for more info')
            return
        debug('sending "{0}"...'.format(msg))
        try:
            self.convore.send_message(self.topic, msg)
        except NetworkError, e:
            error(unicode(e))

