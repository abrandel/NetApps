from watson_developer_cloud import TextToSpeechV1

text_to_speech = TextToSpeechV1(
    iam_apikey='po9VttMkdr1VKeu9ATubNgEMr2idjqu-ce-6ZiIhtpt6',
    url='https://stream.watsonplatform.net/text-to-speech/api'
)

with open('hello_world_checking.wav', 'wb') as audio_file:
    audio_file.write(
        text_to_speech.synthesize(
            'Hello world checking',
            'audio/wav',
            'en-US_AllisonVoice'
        ).get_result().content)
