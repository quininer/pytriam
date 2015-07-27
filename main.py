#!/usr/bin/env python
# encoding: utf-8

from lib import Messager

im = Messager("./config.json")

@im.on('tox.init')
def init(this ,arguments):
    print("ID: {}".format(this.core.self_get_address()))

@im.on('tox.connect')
def status(this, arguments):
    print("{} to Tox Network.".format(arguments.get('status')))

@im.on('friend.request')
def frequest(this, arguments):
    print("friend request, {} {}".format(
        arguments.get('pk'),
        arguments.get('message')
    ))
    this.core.friend_add_norequest(arguments.get('pk'))

@im.on('friend.message')
def friend_message(this, arguments):
    this.core.friend_send_message(
        arguments.get('fid'),
        arguments.get('message')
    )

@im.on('group.invite')
def group_invite(this, arguments):
    this.core.join_groupchat(
        arguments.get('fnum'),
        arguments.get('data')
    )

@im.on('group.message.normal')
def group_message(this, arguments):
    if arguments.get('message').startswith('[LQYMGT]'):
        this.core.group_message_send(
            arguments.get('gnum'),
            "LQYMGT: 好棒！"
        )

if __name__ == '__main__':
    try:
        im.run()
    except KeyboardInterrupt:
        im.save()
