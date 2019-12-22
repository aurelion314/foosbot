from foosbot.modules.slack import Slack

def start(data, account_id, reader_id):
    import foosbot.database as database
    from datetime import datetime, timedelta
    db = database.builder('foosbot')

    #New game starting. There should be no in progress games. If there are, set it to failed.
    in_progress_matches = db.table('matches').where('account_id', account_id).where('reader_id', reader_id).where('status', 'in_progress').get()
    for in_progress_match in in_progress_matches:
        Slack.clear_match(in_progress_match)
        db.table('matches').where('account_id', account_id).where('status', 'in_progress').where('id', in_progress_match['id']).update({'status':'failed', 'updated_at': str(datetime.now())})

    match = {
        'account_id': account_id,
        'reader_id': reader_id,
        'player1': data['player1'],
        'player2': data['player2'],
        'status': 'in_progress',
        'created_at': str(datetime.now()),
    }

    res = db.table('matches').insert_get_id(match)
    match['id'] = res

    #return results
    if res:
        try: 
            Slack.new_match(match)
        except Exception as e:
            print (e)
        return {'status': 'success'}
    else:
        return {'status': 'failed'}