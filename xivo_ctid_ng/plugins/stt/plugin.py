# Copyright 2019-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_amid_client import Client as AmidClient
from xivo_confd_client import Client as ConfdClient

from .notifier import SttNotifier
from .bus_consumer import SttBusEventHandler


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        bus_consumer = dependencies['bus_consumer']
        bus_publisher = dependencies['bus_publisher']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        notifier = SttNotifier(bus_publisher)
        bus_event_handler = SttBusEventHandler(notifier)
        bus_event_handler.subscribe(bus_consumer)

