from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def input(request, client_id):
    return render(request, 'foosbot/input.html')

def leaderboard(request, client_id):
    return render(request, 'foosbot/leaderboard.html')

def verify_hash(request, client_id, secret):
    from orator import DatabaseManager
    import foosbot.database as database
    db = database.builder('foosbot')
    # newd = {'id': client_id, 'name':'McTesterson', 'secret':'test!'}
    # res = db.table('clients').insert(newd)
    res = db.table('clients').where('client_id', client_id).first()
    # res = db.table('clients').first()
    print(res)
    if not res: return HttpResponse('Client not found: '+str(client_id))
    if res['secret'] != secret: return('Invalid key')
    
    #Looks good. Authenticate them and redirect to input page.
    return redirect(input, client_id=client_id)
    return HttpResponse(secret)

@csrf_exempt
def handler(request, client_id):
    from foosbot.modules.handler import Handler
    from json import dumps

    hand = Handler(request, client_id)
    response = hand.handle(request)
    return HttpResponse(dumps(response)) if response else HttpResponseBadRequest()