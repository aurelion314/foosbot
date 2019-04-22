import requests, json

def say(data):
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
            "name": "en-GB-Standard-A"
        }
    }

    #ping google
    url = 'https://texttospeech.googleapis.com/v1/text:synthesize?key=AIzaSyC5_MLIKaakmLzOBGJNulIKUS89FqRh4I0'

    response = requests.post(url, json=data)
    r = response.json()
    if 'audioContent' in r:
        return {'status':'success', 'result':r['audioContent']}
    else:
        return {'status':'failed', 'result':str(r)}