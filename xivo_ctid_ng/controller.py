# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from threading import Thread
from functools import partial
from xivo import plugin_helpers
from xivo.config_helper import get_xivo_uuid
from xivo.consul_helpers import ServiceCatalogRegistration
from xivo.status import StatusAggregator, TokenStatus
from xivo.token_renewer import TokenRenewer
from xivo_auth_client import Client as AuthClient

from .ari_ import CoreARI
from .bus import CoreBusConsumer
from .bus import CoreBusPublisher
from .collectd import CoreCollectd
from .rest_api import api, adapter_api, CoreRestApi
from .service_discovery import self_check

logger = logging.getLogger(__name__)


class Controller:

    def __init__(self, config):
        xivo_uuid = get_xivo_uuid(logger)
        auth_config = dict(config['auth'])
        auth_config.pop('key_file', None)
        auth_client = AuthClient(**auth_config)
        self.ari = CoreARI(config['ari'])
        self.bus_publisher = CoreBusPublisher(config)
        self.bus_consumer = CoreBusConsumer(config)
        self.collectd = CoreCollectd(config)
        self.rest_api = CoreRestApi(config)
        self.status_aggregator = StatusAggregator()
        self.token_renewer = TokenRenewer(auth_client)
        self.token_status = TokenStatus()
        self._service_registration_params = ['xivo-ctid-ng',
                                             xivo_uuid,
                                             config['consul'],
                                             config['service_discovery'],
                                             config['bus'],
                                             partial(self_check,
                                                     config['rest_api']['port'])]
        plugin_helpers.load(
            namespace='xivo_ctid_ng.plugins',
            names=config['enabled_plugins'],
            dependencies={
                'api': api,
                'adapter_api': adapter_api,
                'ari': self.ari,
                'bus_publisher': self.bus_publisher,
                'bus_consumer': self.bus_consumer,
                'collectd': self.collectd,
                'config': config,
                'status_aggregator': self.status_aggregator,
                'token_changed_subscribe': self.token_renewer.subscribe_to_token_change,
                'next_token_changed_subscribe': self.token_renewer.subscribe_to_next_token_change,
            }
        )

    def run(self):
        logger.info('xivo-ctid-ng starting...')
        self.token_renewer.subscribe_to_token_change(self.token_status.token_change_callback)
        self.status_aggregator.add_provider(self.ari.provide_status)
        self.status_aggregator.add_provider(self.bus_consumer.provide_status)
        self.status_aggregator.add_provider(self.token_status.provide_status)
        bus_producer_thread = Thread(target=self.bus_publisher.run, name='bus_producer_thread')
        bus_producer_thread.start()
        collectd_thread = Thread(target=self.collectd.run, name='collectd_thread')
        collectd_thread.start()
        bus_consumer_thread = Thread(target=self.bus_consumer.run, name='bus_consumer_thread')
        bus_consumer_thread.start()
        ari_thread = Thread(target=self.ari.run, name='ari_thread')
        ari_thread.start()
        try:
            with self.token_renewer:
                with ServiceCatalogRegistration(*self._service_registration_params):
                    self.rest_api.run()
        finally:
            logger.info('xivo-ctid-ng stopping...')
            self.ari.stop()
            self.bus_consumer.should_stop = True
            self.collectd.stop()
            self.bus_publisher.stop()
            logger.debug('joining ari thread')
            ari_thread.join()
            logger.debug('joining bus consumer thread')
            bus_consumer_thread.join()
            logger.debug('joining collectd thread')
            collectd_thread.join()
            logger.debug('joining bus producer thread')
            bus_producer_thread.join()
            logger.debug('joining rest api threads')
            self.rest_api.join()
            logger.debug('done joining')

    def stop(self, reason):
        logger.warning('Stopping xivo-ctid-ng: %s', reason)
        self.rest_api.stop()
