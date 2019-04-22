from datetime import datetime
#remove match 
def remove(data):
    db.table('match').where('status', 'in_progress').update({'status':'failed', 'updated_at': str(datetime.now())})