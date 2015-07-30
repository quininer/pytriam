#!/usr/bin/env python
# encoding: utf-8

from pytriam import Messager


im = Messager("./config.json")


@im.on('tox.init')
def init(this, args):
    print("ID: {}".format(this.id))


@im.on('tox.connect')
def status(this, args):
    print("{} to Tox Network.".format(args.get('status')))


@im.on('friend.request')
def frequest(this, args):
    print("friend request, {} {}".format(
        args.get('target'),
        args.get('message')
    ))
    this.core.friend_add_norequest(args.get('target'))


@im.on('friend.message')
def friend_message(this, args):
    this.send(
        args.get('target'),
        args.get('message')
    )


@im.on('group.invite.text')
def group_invite(this, args):
    this.join(
        args.get('target'),
        args.get('data')
    )


@im.on('group.message.normal')
def group_message(this, args):
    this.group(args.get('target')).send(args.get('message'))

if __name__ == '__main__':
    try:
        im.run()
    except KeyboardInterrupt:
        im.save()
