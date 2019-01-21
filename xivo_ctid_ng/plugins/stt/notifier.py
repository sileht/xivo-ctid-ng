# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.conference.event import (
    HelloWorldEvent,
)

class HelloWorldEvent(object):
    name = 'hello_world'

    def __init__(self):
        # self.required_acl = 'events.stt.hello_world'
        self.routing_key = 'stt.hello_world'

    def marshal(self):
        result = dict()
        result['hello'] = "world"
        return result

    @classmethod
    def unmarshal(cls, msg):
        return cls()


class SttNotifier:

    def __init__(self, bus_producer):
        self._bus_producer = bus_producer

    def hello_world(self):
        event = HelloWorldEvent()
        self._bus_producer.publish(event)
