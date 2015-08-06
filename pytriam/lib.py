#!/usr/bin/env python
# encoding: utf-8

from os.path import isfile
import time

from pytox import Tox, ToxAV


class ToxOptions():
    def __init__(self):
        self.ipv6_enabled = True
        self.udp_enabled = True
        self.proxy_type = 0  # 1=http, 2=socks
        self.proxy_host = ''
        self.proxy_port = 0
        self.start_port = 0
        self.end_port = 0
        self.tcp_port = 0
        self.savedata_type = 0  # 1=toxsave, 2=secretkey
        self.savedata_data = b''
        self.savedata_length = 0


class Av(ToxAV):
    def __init__(self, core, max_calls):
        pass


class Core(Tox):
    def __init__(self, messager, bot, bootstrap):
        options = ToxOptions()

        if isfile(bot.get('profile', './profile.tox')):
            data = open(bot.get('profile', './profile.tox'), 'rb').read()
            options.savedata_data = data
            options.savedata_length = len(data)
            options.savedata_type = 1

        super().__init__(options)

        self.messager = messager
        self.av = Av(self, 12)
        self.bootstrap(
            bootstrap.get('ip', '127.0.0.1'),
            bootstrap.get('port', 33445),
            bootstrap.get('key')
        )
        self.self_set_name(bot.get('name', 'triam'))
        self.self_set_status_message(bot.get('status', 'A4.'))

    def on_group_namelist_change(self, group_number, peer_number, change):
        pass

    def on_file_send_request(
        self, friend_number, file_number, file_size, filename
    ):
        pass

    def on_file_control(
        self, friend_number, receive_send, file_number, control_type, data
    ):
        pass

    def on_file_data(friend_number, file_number, data):
        pass

    def on_file_recv(
        self, friend_number, file_number, kind,
        file_size, filename, filename_length
    ):
        pass

    def on_file_recv_control(self, friend_number, file_number, control):
        pass

    def on_file_recv_chunk(
        self, friend_number, file_number, position, data, length
    ):
        pass

    def on_friend_request(self, public_key, message):
        """
        friend request event.
            - public_key    friend public key.
            - message       request message.

        friend.request:
            | target        target, public key.
            | message       request message.
        """
        self.messager.trigger('friend.request', {
            'target': public_key,
            'message': message
        })

    def on_group_invite(self, friend_number, kind, group_public_key):
        """
        group invite event.
            - friend_number     friend number.
            - kind              group type. (0 | 1)
            - group_public_key  group public key.

        group.invite:
            | target            friend number.
            | type              group type. (text | audio)
            | data              group public key.
        """
        self.messager.trigger('group.invite', {
            'target': friend_number,
            'kind': ('text', 'audio')[kind],
            'data': group_public_key
        })
        self.messager.trigger(
            'group.invite.{}'.format(('text', 'audio')[kind]),
            {
                'target': friend_number,
                'data': group_public_key
            }
        )

    def on_group_message(self, group_number, peer, message):
        """
        group message event.
            - group_number          group number.
            - peer                  friend number on group.
            - message               group message.

        group.message:
            * group message, not from self
            | kind                  message type.
        group.message.normal:
            * only normal message

            | target                group number.
            | peer                  friend number on group.
            | message               group normal message.
        """
        if self.group_peername(group_number, peer) == self.self_get_name():
            return
        self.messager.trigger('group.message', {
            'target': group_number,
            'peer': peer,
            'kind': 'normal',
            'message': message
        })
        self.messager.trigger('group.message.normal', {
            'target': group_number,
            'peer': peer,
            'message': message
        })

    def on_group_action(self, group_number, peer, message):
        """
        group message event.
            - group_number          group number.
            - peer                  friend number on group.
            - message               group message.

        group.message:
            * group message, not from self
            | kind                  message type.
        group.message.normal:
            * only action message

            | target                group number.
            | peer                  friend number on group.
            | message               group action message.
        """
        if self.group_peername(group_number, peer) == self.self_get_name():
            return
        self.messager.trigger('group.message', {
            'target': group_number,
            'peer': peer,
            'kind': 'action',
            'message': message
        })
        self.messager.trigger('group.message.action', {
            'target': group_number,
            'peer': peer,
            'message': message
        })

    def on_friend_message(self, friend_number, message):
        """
        friend message.
            - friend_number friend number
            - message       message

        friend.message:
            | target        friend number
            | message       message
        """
        self.messager.trigger('friend.message', {
            'target': friend_number,
            'message': message
        })

    def on_friend_connection_status(self, friend_number, status):
        """
        friend connection status.
            - friend_number     friend number
            - status            connection status

        friend.status:
            | target            friend number
            | status            connection status
        """
        self.messager.trigger('friend.status', {
            'target': friend_number,
            'status': status
        })

    def loop(self):
        self.messager.trigger('tox.init', {})
        checked = False

        while True:
            status = self.self_get_connection_status()

            self.messager.trigger('tox.iter', {})

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

            try:
                self.iterate()
            except UnicodeDecodeError as err:
                #  HACK this is PyTox bug.
                print("warning: {!r}".format(err))

            time.sleep(0.01)
