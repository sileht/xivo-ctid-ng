# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os
from concurrent.futures import ThreadPoolExecutor
import functools
import logging

from websocket import WebSocketApp
from .transcribe_streaming import transcribe_streaming

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

logger = logging.getLogger(__name__)

APP_NAME = "wazo-app-stt"


class SttStasis:

    def __init__(self, config, ari, notifier):
        self._config = config
        self._ari = ari.client
        self._notifier = notifier
        self._threadpool = ThreadPoolExecutor(max_workers=10)
        self._speech_client = speech.SpeechClient.from_service_account_file(config["stt"]["google_creds"])
        self._streaming_config = types.StreamingRecognitionConfig(
            config=types.RecognitionConfig(
                encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code='fr-FR'))

    def initialize(self):
        self._ari.on_channel_event('StasisStart', self.stasis_start)
        logger.debug('Stasis stt initialized')

    def stasis_start(self, event_objects, event):
        logger.critical("event_objects: %s", event_objects)
        logger.critical("event: %s", event)
        f = self._threadpool.submit(self._handle_call, event_objects)
        logger.critical("thread started")

    def _handle_call(self, event_objects):
        channel = event_objects["channel"]
        ws = WebSocketApp(self._config["stt"]["ari_websocket_stream"],
                          header={"Channel-ID": channel.id},
                          subprotocols=["stream-channel"],
                          on_message=functools.partial(self._on_message,
                                                       channel=channel)
                          )
        logger.critical("websocket client started")
        ws.run_forever()

    def _on_message(self, ws, message, channel=None):
        # In practice, stream should be a generator yielding chunks of audio data.
        logger.critical("_on_message")

        if self._config["stt"].get("dump_dir"):
            try:
                os.makedirs(self._config["stt"]["dump_dir"])
            except OSError:
                pass
            fpath = "%s/wazo-stt-dump-%s.pcm" % (self._config["stt"]["dump_dir"], channel.id)
            with open(fpath, "wb") as f:
                f.write(message)

        stream = [message]
        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in stream)

        responses = list(self._speech_client.streaming_recognize(
            self._streaming_config, requests))

        logger.critical("responses: %d" % len(responses))
        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. The other results will be for subsequent portions of
            # the audio.
            results = list(response.results)
            logger.critical("results: %d" % len(results))
            for result in results:
                if result.is_final:
                    result_stt = result.alternatives[0].transcript
                    logger.critical("test: %s", result_stt)
                    channel.setChannelVar(variable="X_WAZO_STT", value=result_stt)
                    self._notifier.publish_stt(channel.id, result_stt)
