import foosbot.database as database
import requests
import json


class Slack:
    def post_message(slack_connection, data):
        db = database.builder('foosbot')
        data['token'] = slack_connection['token']
        data['channel'] = slack_connection['channel']
        
        url = "https://slack.com/api/chat.postMessage"

        r = Slack.call(url, data)
        return json.loads(r.content)


    def new_match(match):
        db = database.builder('foosbot')
        #first see if they have slack configured.
        slack_connection = db.table('slack_connections').where('account_id', match['account_id']).first()
        if not slack_connection: return False

        #get player names
        player1 = db.table('users').where('id', match['player1']).select('fname').first()['fname']
        player2 = db.table('users').where('id', match['player2']).select('fname').first()['fname']

        data = {
            "text": "*"+player1 +" vs " +player2 +"*",
            "attachments": json.dumps([{"text": "Match Started! ", "color": "warning"}]),
        }

        r = Slack.post_message(slack_connection, data)
        if r:
            record = {'account_id': slack_connection['account_id'], 'slack_connection':slack_connection['id'], 'match':match['id']}
            record['timestamp'] = r['ts']
            record['data'] = json.dumps({'text':data['text'], 'attachments':data.get('attachments')})
            db.table('slack_records').insert(record)


    def end_match(match_id, winner, loser, streak, points):
        db = database.builder("foosbot")
        slack_record = db.table("slack_records").where("match", match_id).first()
        if not slack_record:
            return False
        
        slack_connection = db.table('slack_connections').where('id', slack_record['slack_connection']).first()
        if not slack_connection: return False#In case they remove the connection mid match, don't throw an error.

        win_message = winner['fname'] + " Won! (+"+str(points)+" points)"
        if streak > 1:
            win_message += " - That's "+str(streak)+" in a row!"
        
        data = json.loads(slack_record["data"])
        data['ts'] = slack_record['timestamp']
        data["attachments"] = json.dumps([
            {"text": "Match Complete!", "color": "good"},
            {"text": win_message, "color": "good"},
        ])

        r = Slack.updateMessage(slack_connection, data)

    def clear_match(match):
        db = database.builder('foosbot')
        #Is there a record to clear?
        slack_record = db.table('slack_records').where('match', match['id']).first()
        if not slack_record: return True
        #Get slack connection info
        slack_connection = db.table('slack_connections').where('id', slack_record['slack_connection']).first()
        if not slack_connection: return False

        #format slack data
        data = json.loads(slack_record["data"])
        data['ts'] = slack_record['timestamp']
        data["attachments"] = json.dumps([
            {"text": "Match Cleared!", "color": "yellow"},
        ])
        #update
        r = Slack.updateMessage(slack_connection, data)



    def updateMessage(slack_connection, data):
        db = database.builder('foosbot')
        data['token'] = slack_connection['token']
        data['channel'] = slack_connection['channel']
        
        url = "https://slack.com/api/chat.update"

        r = Slack.call(url, data)
        return json.loads(r.content)

    def call(url, data):
        response = requests.get(url, params=data)  # , headers=headers)
        return response


if __name__ == "__main__":
    match = {
        'account_id': 1,
        'player1': data['player1'],
        'player2': data['player2'],
        'status': 'in_progress',
        'created_at': str(datetime.now()),
    }


    # data = {
    #     "token": "xoxp-624952400887-624952401303-620284124833-7146085e8873b92cea0c5f51cf6fa5ed",
    #     "channel": "#foosbot",
    #     "text": "Sewon (#1) vs Mike (#4)",
    #     "attachments": json.dumps(
    #         [{"text": "Match Started! ", "color": "warning"}]
    #     ),
    # }
    # url = base+'chat.update'
    # data = {
    #     "token": "xoxp-624952400887-624952401303-620284124833-7146085e8873b92cea0c5f51cf6fa5ed",
    #     'channel':'CJD8FA1N2',
    #     'ts':'1560128593.000600',
    #     "text": "Sewon (#1) vs Mike (#3)",
    #     "attachments": json.dumps([
    #         {
    #             "text": "Match Complete!",
    #             "color":"good"
    #         },
    #         {
    #             "text": "Mike Won! Thats 4 in a row! (3 of 3 today)",
    #             "color":"good"
    #         }
    #     ])
    # }