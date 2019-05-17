from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from json import dumps, loads
from datetime import datetime

import foosbot.database as database

def input(request, account_id):
    if request.session.get('account_id') != account_id: raise PermissionDenied
    return render(request, 'foosbot/input.html', context={'account_id':account_id})

def leaderboard(request, account_id):
    if not request.user.is_authenticated or request.user.account != account_id: raise PermissionDenied
    db = database.builder('foosbot')
    account = db.table('accounts').where('id', account_id).first()
    if not account: return HttpResponseNotFound()
    #redirect to the token based leaderboard to keep render logic in one place
    return redirect(leaderboard_token, token=account['token'])

def leaderboard_token(request, token):
    db = database.builder('foosbot')
    account = db.table('accounts').where('token', token).first()
    if not account: return HttpResponseNotFound()

    players = db.table('users').where('account_id', account.id).where_null('deleted_at').order_by('elo', 'desc').get()
    return render(request, 'foosbot/leaderboard.html',context={'players':players, 'account_id':account['id'], 'account_name':account['name']})

def setup(request, account_id):
    if not request.user.is_authenticated: return redirect(login)
    if request.user.account != account_id: raise PermissionDenied
    db = database.builder('foosbot')
    account = db.table('accounts').where('id', request.user.account).first()
    if account:
        return render(request, 'foosbot/setup.html', context={'account_name': account.name, 'account_id':account_id, 'slack_url': account.slack_url, 'slack_config_url':account.slack_config_url, 'slack_channel': account.slack_channel})
    else:
        return HttpResponseNotFound()

def slack(request):
    r = request.GET
    print(r)

    data = {}
    data['code'] = r['code']
    data['client_id'] = '624952400887.615198951842'
    data['client_secret'] = 'd91d4794d106de4db1957c2f274346ae'
    # data['redirect_uri'] = 'https://www.employeearcade.com/slack/'
    
    print(data)

    import requests
    res = requests.get('https://slack.com/api/oauth.access', data)
    res = res.json()

    print(res)
    account_id = request.user.account
    slack_url = res['incoming_webhook']['url']
    slack_channel = res['incoming_webhook']['channel']
    slack_config_url = res['incoming_webhook']['configuration_url']

    #Add config url and channel name somewhere. Accounts table or new slack table

    db = database.builder('foosbot')
    db.table('accounts').where('id', account_id).update({'slack_url':slack_url, 'slack_config_url': slack_config_url, 'slack_channel': slack_channel})

    #return custom page with link to setup, or redirect to setup
    return HttpResponse('Added channel '+str(slack_channel))


@csrf_exempt
def remove_slack(request, account_id):
    if not request.user.is_authenticated or request.user.account != account_id: raise PermissionDenied
    db = database.builder('foosbot')

    db.table('accounts').where('id', account_id).update({'slack_url':None, 'slack_config_url': None, 'slack_channel': None})
    return HttpResponse(dumps({'status':'success'}))

@csrf_exempt
def player(request, account_id):
    if not request.user.is_authenticated or request.user.account != account_id: raise PermissionDenied
    db = database.builder('foosbot')

    #Patch to modify players
    if request.method == 'PATCH':
        r = loads(request.body)
        #Patch means update or insert
        if r['action'] == 'patch':
            player = r['player']
            player_data = {'account_id':account_id ,'fname':player['fname'].strip(), 'lname':player['lname'].strip(), 'rfid':player['rfid'], 'photo': player['photo'].strip()}
        
            #Check if this is an update or new player
            if player.get('id'):
                existing = db.table('users').where('account_id', account_id).where('id', player['id']).first()
                db.table('users').where('id', existing['id']).update(player_data)
            else: #player not in DB. insert it.
                #First make sure this rfid isn't taken.
                taken = db.table('users').where('account_id', account_id).where('rfid', player['rfid']).exists()
                if taken:
                    return HttpResponse(dumps({'status':'rfid taken or invalid'}))

                from foosbot.modules.player import create_player
                create_player(player_data)
        
        #Delete
        elif r['action'] == 'delete':
            player = r['player']
            db.table('users').where('account_id', account_id).where('id', player['id']).update({'deleted_at':datetime.now(), 'rfid':None})

        #no action? FAILURE
        else:
            return HttpResponse(dumps({'status':'failed'}))

        return HttpResponse(dumps({'status':'success'}))

    #if it wasn't a patch job, then its a query for player list
    players = db.table('users').where('account_id', request.user.account).where_null('deleted_at').order_by('fname', 'asc').get()
    
    data = [{'id':p.id, 'fname':p.fname, 'lname':p.lname, 'photo':p.photo, 'rfid':p.rfid} for p in players]
    return HttpResponse(dumps({'status':'success', 'result':data}))


@csrf_exempt
def login(request):

    if request.method=='GET':
        # from foosbot.models import User
        # user=User.objects.create_user('evan', password='hello')
        # user.is_superuser=False
        # user.is_staff=True
        # user.save()

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

def verify_token(request, account_id):
    r = request.GET
    token = r.get('token')

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
