import requests, json

def slack(data, account_id):
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

    #ping slack
    url = 'https://texttospeech.googleapis.com/v1/text:synthesize?key=AIzaSyC5_MLIKaakmLzOBGJNulIKUS89FqRh4I0'

    response = requests.post(url, json=data)
    r = response.json()

    if 'audioContent' in r:
        return {'status':'success'}
    else:
        return {'status':'failed', 'result':str(r)}