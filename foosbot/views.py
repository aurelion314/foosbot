from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from json import dumps

import foosbot.database as database


def input(request, account_id):
    if request.session.get('account_id') != account_id: raise PermissionDenied
    return render(request, 'foosbot/input.html', context={'account_id':account_id})

def leaderboard(request, account_id):
    db = database.builder('foosbot')
    players = db.table('users').order_by('points', 'desc').get()
    return render(request, 'foosbot/leaderboard.html',context={'players':players, 'account_id':account_id})

def setup(request, account_id):
    if not request.user.is_authenticated or request.user.account != account_id: raise PermissionDenied
    db = database.builder('foosbot')
    account = db.table('accounts').where('id', request.user.account).first()
    if account:
        return render(request, 'foosbot/setup.html', context={'account_name': account.name, 'account_id':account_id})
    else:
        return HttpResponseNotFound()

@csrf_exempt
def player(request, account_id):
    if not request.user.is_authenticated or request.user.account != account_id: raise PermissionDenied
    db = database.builder('foosbot')
    players = db.table('users').where('account_id', request.user.account).order_by('fname', 'asc').get()
    print(players[0])
    data = [{'fname':p.fname, 'lname':p.lname, 'photo':p.photo, 'rfid':p.rfid} for p in players]
    return HttpResponse(dumps({'status':'success', 'result':data}))


@csrf_exempt
def login(request):

    if request.method=='GET':
        from django.contrib.auth.models import User
        #check if they are already logged in, and return setup page 
        if request.user.is_authenticated and request.user.account:
            return redirect(setup, account_id=int(request.user.account or 0))
        #else goto login page
        return render(request,'foosbot/login.html')
    else:
        r = request.POST
        username = r.get('username')
        password = r.get('password')

        from django.contrib.auth import authenticate, login
        user = authenticate(username = username, password = password)
        if user is not None:
            if not user.account: return HttpResponse(dumps({'status':'User is not connected to an account'}))
            login(request, user)
            return HttpResponse(dumps({'status':'success', 'account_id':user.account}))
        
        return HttpResponse(dumps({'status':'User not found'}))

@csrf_exempt
def leaderboard_details(request, account_id):
    from foosbot.modules.leaderboard import get_details
    r = request.POST
    player_id = r['player']

    data = get_details(account_id, player_id)
    
    return render(request, 'foosbot/details.html',context=data)

def verify_hash(request, account_id, token):
    db = database.builder('foosbot')
    # newd = {'id': account_id, 'name':'McTesterson', 'token':'test'}
    # res = db.table('accounts').insert(newd)
    res = db.table('accounts').where('id', account_id).first()
    
    if not res: return HttpResponse('Client not found: '+str(account_id))

    if res['token'] != token: return HttpResponse('Invalid Token')
    
    #Looks good. Authenticate them and redirect to input page.
    request.session['account_id'] = account_id
    request.session.set_expiry(360000000)

    # return HttpResponse('Success')
    return redirect(input, account_id=account_id)

@csrf_exempt
def handler(request, account_id):
    #Verify they are allowed in here.
    if request.session.get('account_id') != account_id: raise PermissionDenied

    from foosbot.modules.handler import Handler

    hand = Handler(request, account_id)
    response = hand.handle(request)
    return HttpResponse(dumps(response)) if response else HttpResponseBadRequest()
