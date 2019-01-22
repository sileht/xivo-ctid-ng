# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from websocket import create_connection, WebSocketException
from .transcribe_streaming import transcribe_streaming

logger = logging.getLogger(__name__)

APP_NAME = "wazo-app-stt"


class SttStasis:

    def __init__(self, ari, notifier):
        self._ari = ari.client
        self._notifier = notifier

    def initialize(self):
        self._ari.on_channel_event('StasisStart', self.stasis_start)
        logger.debug('Stasis stt initialized')

    def stasis_start(self, event_objects, event):
        logger.critical("event_objects: %s", event_objects)
        logger.critical("event: %s", event)
        channel = event_objects["channel"]

        for result_stt in self.get_text(channel.id):
            logger.critical("test: %s", result_stt)
            channel.setChannelVar(variable="X_WAZO_STT", value=result_stt)
            self._notifier.publish_stt(channel.id, result_stt)


    def get_text(self, channel_id):
        ws = create_connection("ws://websocket-stt:8765/stream",
                               header={"Channel-ID": channel_id})
        logger.critical("create done")
        return transcribe_streaming(ws)
