# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

logger = logging.getLogger(__name__)

APP_NAME = "wazo-app-stt"


class SttStasis:

    def __init__(self, ari, notifier):
        self._ari = ari.client
        self._core_ari = ari
        self._notifier = notifier

    def initialize(self):
        self._ari.on_channel_event('StasisStart', self.stasis_start)
        self._core_ari.register_application(APP_NAME)
        self._core_ari.reload()
        logger.debug('Stasis stt initialized')

    def stasis_start(self, event_objects, event):
        if event["application"] != APP_NAME:
            return
        logger.critical("event_objects: %s", event_objects)
        logger.critical("event: %s", event)
        channel = event_objects["channel"]

        ## ....

        stt_result = "crise cardiaque (%s)" % channel.id

        self._notifier.publish_stt(channel.id, stt_result)
