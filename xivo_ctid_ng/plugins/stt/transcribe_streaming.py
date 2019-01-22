#!/usr/bin/env python

import argparse
import io

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/creds.json"

# [START speech_transcribe_streaming]
def transcribe_streaming(ws):
    """Streams transcription of the given audio file."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='fr-FR')
    streaming_config = types.StreamingRecognitionConfig(config=config)

    # [START speech_python_migration_streaming_request]
    while True:
        content = ws.recv()
        if not content:
            break

        # In practice, stream should be a generator yielding chunks of audio data.
        stream = [content]
        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in stream)

        # streaming_recognize returns a generator.
        # [START speech_python_migration_streaming_response]
        responses = client.streaming_recognize(streaming_config, requests)
        # [END speech_python_migration_streaming_request]

        for response in responses:
            # Once the transcription has settled, the first result will contain the
            # is_final result. The other results will be for subsequent portions of
            # the audio.
            for result in response.results:
                if result.is_final:
                    yield result.alternatives[0].transcript

#                print('Finished: {}'.format(result.is_final))
#                print('Stability: {}'.format(result.stability))
#                alternatives = result.alternatives
#                # The alternatives are ordered from most likely to least.
#                for alternative in alternatives:
#                    print('Confidence: {}'.format(alternative.confidence))
#                    print(u'Transcript: {}'.format(alternative.transcript))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('stream', help='File to stream to the API')
    args = parser.parse_args()
    transcribe_streaming(args.stream)
