#!/usr/bin/env python

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/creds.json"

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

# [START speech_transcribe_streaming]
def transcribe_streaming(ws):
    """Streams transcription of the given audio file."""
    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='fr-FR')
    streaming_config = types.StreamingRecognitionConfig(config=config)

    while True:
        content = ws.recv()
        if not content:
            break

        # In practice, stream should be a generator yielding chunks of audio data.
        stream = [content]
        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in stream)

        responses = client.streaming_recognize(streaming_config, requests)

        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. The other results will be for subsequent portions of
            # the audio.
            for result in response.results:
                if result.is_final:
                    yield result.alternatives[0].transcript
