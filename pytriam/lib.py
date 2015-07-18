#!/usr/bin/env python
# encoding: utf-8

from os.path import exists
from json import loads
from time import sleep

from pytox import Tox, ToxAV

class ToxOptions():
    def __init__(self):
        self.ipv6_enabled = True
        self.udp_enabled = True
        self.proxy_type = 0 # 1=http, 2=socks
        self.proxy_host = ''
        self.proxy_port = 0
        self.start_port = 0
        self.end_port = 0
        self.tcp_port = 0
        self.savedata_type = 0 # 1=toxsave, 2=secretkey
        self.savedata_data = b''
        self.savedata_length = 0

class Av(ToxAV):
    pass

class Core(Tox):
    def __init__(self, messager, bot, bootstrap):
        options = ToxOptions()

        if exists(bot.get('profile') or "./profile.tox"):
            data = open(bot.get('profile') or "./profile.tox", 'rb').read()
            options.savedata_data = data
            options.savedata_length = len(data)
            options.savedata_type = 1

        super().__init__(options)

        self.messager = messager
        self.av = Av(self, 12)
        self.bootstrap(
            bootstrap.get('ip') or '127.0.0.1',
            bootstrap.get('port') or 33445,
            bootstrap.get('key')
        )
        self.self_set_name(bot.get('name') or 'triam')
        self.self_set_status_message(bot.get('status') or 'A4.')

    def on_friend_request(self, pk, message):
        self.messager.trigger('friend.request', {
            'pk': pk,
            'message': message
        })

    def on_group_invite(self, fnum, kind, data):
        self.messager.trigger('group.invite', {
            'fnum': fnum,
            'kind': kind,
            'data': data
        })

    def on_group_message(self, gnum, fgnum, message):
        self.messager.trigger('group.message', {
            'gnum': gnum,
            'fgnum': fgnum,
            'message': message
        })
        self.messager.trigger('group.message.normal', {
            'gnum': gnum,
            'fgnum': fgnum,
            'message': message
        })

    def on_group_action(self, gnum, fgnum, message):
        self.messager.trigger('group.message', {
            'gnum': gnum,
            'fgnum': fgnum,
            'message': message
        })
        self.messager.trigger('group.message.action', {
            'gnum': gnum,
            'fgnum': fgnum,
            'message': message
        })

    def on_friend_message(self, fid, message):
        self.messager.trigger('friend.message', {
            'fid': fid,
            'message': message
        })

    def on_friend_connection_status(self, fid, status):
        self.messager.trigger('friend.status', {
            'fid': fid,
            'status': status
        })

    def loop(self):
        self.messager.trigger('tox.init', {})
        checked = False

        while True:
            status = self.self_get_connection_status()

            if not checked and status:
                self.messager.trigger('tox.connect', {
                    'status': "Connected"
                })
                checked = True

            if checked and not status:
                self.messager.trigger('tox.connect', {
                    'status': "Disconnected"
                })
                checked = False

            self.iterate()
            sleep(0.01)

class Messager(object):
    def __init__(self, path):
        config = loads(open(path).read())
        self.bot = config.get('bot') or {}
        self.bootstrap = config.get('bootstrap') or {}
        self.events = {}

        self.core = Core(self, self.bot, self.bootstrap)

    def save(self):
        open(
            self.bot.get('profile') or "./profile.tox",
            'wb'
        ).write(self.core.get_savedata())

    def on(self, name):
        def on_event(fn):
            if name not in self.events:
                self.events[name] = list()
            self.events[name].append(fn)
        return on_event

    def trigger(self, name, arguments):
        for fn in self.events.get(name) or []:
            fn(self, arguments)

    def run(self):
        self.core.loop()
