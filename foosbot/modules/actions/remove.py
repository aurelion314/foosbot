from datetime import datetime
import foosbot.database as database
from foosbot.modules.slack import Slack

#remove match 
def remove(data, account_id, reader_id):
    db = database.builder('foosbot')
    #are there any floating matches that need clearing?
    matches = db.table('matches').where('account_id', account_id).where('reader_id', reader_id).where('status', 'in_progress').get()
    for match in matches:
        db.table('matches').where('id', match['id']).update({'status':'failed', 'updated_at': str(datetime.now())})
        
        #also update any slack messages.
        Slack.clear_match(match)