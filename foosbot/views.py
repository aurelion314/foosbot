from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import foosbot.database as database

# Create your views here.
def input(request, account_id):
    return render(request, 'foosbot/input.html', context={'account_id':account_id})

def leaderboard(request, account_id):
    db = database.builder('foosbot')
    players = db.table('users').order_by('points', 'desc').get()
    return render(request, 'foosbot/leaderboard.html',context={'players':players, 'account_id':account_id})

@csrf_exempt
def leaderboard_details(request, account_id):
    from foosbot.modules.leaderboard import get_details
    r = request.POST
    player_id = r['player']

    data = get_details(account_id, player_id)
    
    return render(request, 'foosbot/details.html',context=data)

def verify_hash(request, account_id, token):
    db = database.builder('foosbot')
    # newd = {'id': account_id, 'name':'McTesterson', 'token':'test!'}
    # res = db.table('clients').insert(newd)
    res = db.table('clients').where('account_id', account_id).first()
    # res = db.table('clients').first()
    print(res)
    if not res: return HttpResponse('Client not found: '+str(account_id))
    if res['token'] != token: return('Invalid key')
    
    #Looks good. Authenticate them and redirect to input page.
    return redirect(input, account_id=account_id)
    return HttpResponse(secret)

@csrf_exempt
def handler(request, account_id):
    from foosbot.modules.handler import Handler
    from json import dumps

    hand = Handler(request, account_id)
    response = hand.handle(request)
    return HttpResponse(dumps(response)) if response else HttpResponseBadRequest()