import foosbot.database as database
import requests
import json


class Slack:
    def post_message(slack_connection, data):
        db = database.builder('foosbot')
        data['token'] = slack_connection['token']
        data['channel'] = slack_connection['channel_id']
        
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
            print('no slack record for match', match_id)
            return False
        
        slack_connection = db.table('slack_connections').where('id', slack_record['slack_connection']).first()
        if not slack_connection:
            print('no slack connection for match', match_id, 'connection', slack_record['slack_connection'])
            return False#In case they remove the connection mid match, don't throw an error.

        win_message = winner['fname'] + " Won! (+"+str(points)+" points)"
        if streak > 1:
            win_message += " - That's "+str(streak)+" in a row!"
        
        data = json.loads(slack_record["data"])
        data['ts'] = slack_record['timestamp']
        data["attachments"] = json.dumps([
            {"text": "Match Complete!", "color": "good"},
            {"text": win_message, "color": "good"},
        ])

        print('updating slack', data)
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
        data['channel'] = slack_connection['channel_id']
        
        url = "https://slack.com/api/chat.update"

        r = Slack.call(url, data)
        return json.loads(r.content)

    def call(url, data):
        response = requests.get(url, params=data)  # , headers=headers)
        return response


if __name__ == "__main__":

    # data = {
    #     "token": "xoxp-53894058610-138924041447-747388542819-67b1b44912fb9d48d615b68e8618b3de",
    #     "channel": "#foosball_results",
    #     "text": "Mike vs Mike",
    #     "attachments": json.dumps(
    #         [{"text": "Match Started! ", "color": "warning"}]
    #     ),
    # }
    # url = 'https://slack.com/api/chat.postMessage'


    
    data = {
        "token": "xoxp-53894058610-138924041447-747388542819-67b1b44912fb9d48d615b68e8618b3de",
        'channel':'C83RMC3RR',
        'ts':'1568679782.006400',
        "text": "*Jack vs Miker*",
        "attachments": json.dumps([
            {
                "text": "Match Complete!",
                "color":"good"
            },
            {
                "text": "Mike Won!",
                "color":"good"
            }
        ])
    }
    url = 'https://slack.com/api/chat.update'
    r = Slack.call(url, data)
    print(r.content)