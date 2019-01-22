#!/usr/bin/env python

import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types


def transcribe_streaming(content, creds_path):
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/creds.json"

    """Streams transcription of the given audio file."""

    if not content:
        return

    client = speech.SpeechClient.from_service_account_file(creds_path)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='fr-FR')
    streaming_config = types.StreamingRecognitionConfig(config=config)


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
