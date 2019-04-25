from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import foosbot.database as database

# Create your views here.
def input(request, client_id):
    return render(request, 'foosbot/input.html')

def leaderboard(request, client_id):
    db = database.builder('foosbot')
    players = db.table('users').order_by('points', 'desc').get()
    return render(request, 'foosbot/leaderboard.html',context={'players':players, 'client_id':client_id})

@csrf_exempt
def leaderboard_details(request, client_id):
    from foosbot.modules.leaderboard import get_details
    r = request.POST
    player_id = r['player']

    data = get_details(client_id, player_id)
    
    return render(request, 'foosbot/details.html',context=data)

def verify_hash(request, client_id, secret):
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