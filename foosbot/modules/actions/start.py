from foosbot.modules.slack import Slack

def start(data, account_id):
    import foosbot.database as database
    from datetime import datetime, timedelta
    db = database.builder('foosbot')

    #New game starting. There should be no in progress games. If there are, set it to failed.
    db.table('matches').where('account_id', account_id).where('status', 'in_progress').update({'status':'failed', 'updated_at': str(datetime.now())})

    match = {
        'account_id': account_id,
        'player1': data['player1'],
        'player2': data['player2'],
        'status': 'in_progress',
        'created_at': str(datetime.now()),
    }

    res = db.table('matches').insert_get_id(match)
    match['id'] = res

    #return results
    if res:
        Slack.new_match(match)
        return {'status': 'success'}
    else:
        return {'status': 'failed'}