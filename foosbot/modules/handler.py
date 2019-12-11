from django.http import HttpResponse
import foosbot.database as database
from datetime import datetime
import foosbot.modules.actions as actions

class Handler():
    def __init__(self, account_id):
        if not account_id: raise Exception('No account_id provided to handler')
        self.account_id = account_id
    
    def handle(self, request):
        r = request.POST
        action = r['action']
        reader_id = request.session['reader_id']

        if action == 'rfid':
            return actions.rfid(r, self.account_id)
        if action == 'start':
            return actions.start(r, self.account_id, reader_id)
        if action == 'end':
            return actions.end(r, self.account_id, reader_id)
        if action == 'remove':
            return actions.remove(r, self.account_id, reader_id)
        if action == 'say':
            return actions.say(r, self.account_id)
        if action == 'slack':
            return actions.slack(r, self.account_id)
        if action == 'leaderboard':
            import foosbot.modules.leaderboard as leaderboard
            return leaderboard.get_table_leaderboard(r, self.account_id)
        if action == 'ping':
            return self.ping(request)

        return None

    def ping(self, request):
        client_data = []
        for key in request.META:
            if 'HTTP' in key:
                client_data.append({key: request.META[key]})

        # print(client_data)
        #insert ping row with time, account_id, and ping data.
        db = database.builder('foosbot')

        insert_data = {}
        insert_data['account_id'] = self.account_id
        insert_data['reader_id'] = request.session['reader_id']
        insert_data['ip'] = self.get_client_ip(request)
        insert_data['created_at'] = str(datetime.now())
        insert_data['meta_data'] = str(client_data)
        
        db.table('ping').insert(insert_data)

        # sending the following will force a page reload.
        needs_reload = db.table('accounts').where('id', self.account_id).where('refresh_reader', 1).exists()
        if needs_reload: 
            db.table('accounts').where('id', self.account_id).update({'refresh_reader': 0})
            return {'status':'success', 'result':'reload'}
            
        return {'status':'success'}

    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
