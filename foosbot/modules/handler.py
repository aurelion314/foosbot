from django.http import HttpResponse
import foosbot.database as database
from datetime import datetime

class Handler():
    def __init__(self, request, client_id):
        if not client_id: raise Exception('No client_id provided to handler')
        self.client_id = client_id
        self.request = request
    
    def handle(self, request):
        r = request.POST
        action = r['action']

        if action == 'rfid':
            import foosbot.modules.actions as actions
            return actions.rfid(r)
        if action == 'start':
            import foosbot.modules.actions as actions
            return actions.start(r)
        if action == 'end':
            import foosbot.modules.actions as actions
            return actions.end(r)
        if action == 'ping':
            return self.ping(request)

        return None

    def ping(self, request):
        client_data = []
        for key in request.META:
            if 'HTTP' in key:
                client_data.append({key: request.META[key]})

        # print(client_data)
        #insert ping row with time, client_id, and ping data.
        db = database.builder('foosbot')
        db.table('ping').insert({
            'client_id':self.client_id, 
            'ip':self.get_client_ip(request), 
            'time':str(datetime.now()), 
            'meta_data':str(client_data)}
            )

        return 'ping OK'

    def get_client_ip(self,request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
