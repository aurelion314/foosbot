from django.conf import settings as djangoSettings
import requests, json


def say(data, account_id):
    words = data['words']

    data = {
        "audioConfig": {
            "audioEncoding": "LINEAR16",
            "pitch": 0.4,
            "speakingRate": 1
        },
        "input": {
            "text": words
        },
        "voice": {
            "languageCode": "en-GB",
            "name": "en-GB-Wavenet-A"
        }
    }

    #ping google
    url = 'https://texttospeech.googleapis.com/v1/text:synthesize?key=AIzaSyC5_MLIKaakmLzOBGJNulIKUS89FqRh4I0'

    response = requests.post(url, json=data)
    r = response.json()

    if 'audioContent' in r:
        #Save audio to file
        from base64 import b64decode
        audio_path = f'/audio/{account_id}.mp3'
        with open(djangoSettings.STATIC_ROOT+audio_path,'wb') as f:
            f.write(b64decode(r['audioContent']))

        return {'status':'success', 'url':audio_path}
    else:
        return {'status':'failed', 'result':str(r)}