from datetime import datetime
#remove match 
def remove(data, account_id):
    db.table('match').where('account_id', account_id).where('status', 'in_progress').update({'status':'failed', 'updated_at': str(datetime.now())})