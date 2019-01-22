# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)


class SttBusEventHandler:

    def __init__(self, notifier):
        self._notifier = notifier

    def subscribe(self, bus_consumer):
        bus_consumer.on_ami_event('NewChannel', self._on_new_call)

    def _on_new_call(self, event):
        logger.critical("new_call stt %s" % event)
        self._notifier.hello_world()
