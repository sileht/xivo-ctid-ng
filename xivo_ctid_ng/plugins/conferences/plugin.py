# Copyright 2019-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_amid_client import Client as AmidClient
from xivo_confd_client import Client as ConfdClient

from .bus_consume import ConferencesBusEventHandler
from .notifier import ConferencesNotifier
from .resources import ParticipantsResource
from .services import ConferencesService


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        bus_consumer = dependencies['bus_consumer']
        bus_publisher = dependencies['bus_publisher']
        config = dependencies['config']
        token_changed_subscribe = dependencies['token_changed_subscribe']

        amid_client = AmidClient(**config['amid'])
        confd_client = ConfdClient(**config['confd'])

        token_changed_subscribe(amid_client.set_token)
        token_changed_subscribe(confd_client.set_token)

        notifier = ConferencesNotifier(bus_publisher)
        bus_event_handler = ConferencesBusEventHandler(notifier)
        bus_event_handler.subscribe(bus_consumer)
        conferences_service = ConferencesService(amid_client, confd_client)

        api.add_resource(ParticipantsResource, '/conferences/<int:conference_id>/participants', resource_class_args=[conferences_service])
