import requests, json
import foosbot.database as database

def slack(data, account_id):
    return {'status':'failed', 'result':'This method of slack notification is depreciated.'}
    db = database.builder('foosbot')    
    account = db.table('accounts').where('id', account_id).first()
    url = account['slack_url']

    if not url: return {'status':'failed','result':'Slack not configured for this account'}

    message = data['message']

    data = {
        'text': message
    }

    # url = 'https://hooks.slack.com/services/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'

    #ping slack
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        return {'status':'success'}
    else:
        return {'status':'failed', 'result':response.content}