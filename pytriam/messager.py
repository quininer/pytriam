#!/usr/bin/env python
# encoding: utf-8

from json import loads

from .lib import Core


class GroupMessager(object):
    def __init__(self, messager, group_number):
        self.im = messager
        self.core = messager.core
        self.group_number = group_number

    def send(self, message, kind='normal'):
        """
        send message to group.
            - target        group number
            - message       message
            - kind          message type, (normal | actioin)
        """
        {
            'normal': self.core.group_message_send,
            'action': self.core.group_action_send,
        }[kind](
            self.group_number,
            message
        )

    def get_nick(self, target):
        """
        get target nick from group
            - target        friend number on group

            @ nick<str>     target nick
        """
        return self.core.group_peername(
            self.group_number,
            target
        )

    def get_title(self):
        """
        get group title.
            @ title<str>    group title.
        """
        return self.core.group_get_title(self.group_number)

    def set_title(self, title):
        """
        set group title.
            - title     title string.
        """
        self.core.group_set_title(title)


class Messager(object):
    def __init__(self, path):
        config = loads(open(path).read())
        self.bot = config.get('bot', {})
        self.bootstrap = config.get('bootstrap', {})
        self.events = {}

        self.core = Core(self, self.bot, self.bootstrap)

    @property
    def id(self):
        return self.core.self_get_address()

    def set_nick(self, nick):
        self.core.self_set_name(nick)

    def add_friend(self, public_key, message=None):
        if message is None:
            self.core.friend_add_norequest(public_key)
        else:
            self.core.friend_add(public_key, message)

    def group(self, group_number):
        return GroupMessager(self, group_number)

    def join(self, friend_number=None, data=None, kind='text'):
        """
        accept group invite or create group.
            - kind              group type
            - friend_number     inviter friend number
            - data              group public key

            @ group<GroupMessager>
        """
        if not (friend_number or data):
            return self.group(self.core.add_groupchat())

        return self.group({
            'text': self.core.join_groupchat
            # 'audio': self.core.av.join_groupchat
            # XXX PyTox no support
        }[kind](
            friend_number,
            data
        ))

    def send(self, target, message, kind='normal'):
        """
        send message to friend.
            - target        friend number
            - message       message
            - kind          message type, (normal)
        """
        {
            'normal': self.core.friend_send_message,
            # 'action': self.core.friend_send_action
            # XXX PyTox missing
        }[kind](target, message)

    def get_nick(self, target=None):
        """
        get target nick, None is self.
            - target        friend number or None

            @ nick<str>     target nick
        """
        return (
            self.core.self_get_name()
            if target is None else
            self.core.friend_get_name(target)
        )

    def save(self):
        open(
            self.bot.get('profile', './profile.tox'),
            'wb'
        ).write(self.core.get_savedata())

    def on(self, name):
        def on_event(fn):
            if name not in self.events:
                self.events[name] = list()
            self.events[name].append(fn)
        return on_event

    def trigger(self, name, arguments):
        for fn in self.events.get(name,  []):
            fn(self, arguments)

    def run(self):
        self.core.loop()
