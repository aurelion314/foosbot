def rfid(data):
    import foosbot.database as database
    from datetime import datetime, timedelta

    db = database.builder('foosbot')

    rfid = data['rfid']
    #look up rfid 
    # db.table('users').insert({'username': 'proth', 'fname':'Proth', 'rfid':2, 'points':1500})
    player = db.table('users').where('rfid', rfid).first()
    if not player: 
        return {'status':'not found'}

    games = db.table('matches').where('time', '>', str(datetime.now() - timedelta(days=1))).where(
        db.query().where('player1', player['id']).or_where('player2', player['id'])
    ).count()
    wins = db.table('matches').where('time', '>', str(datetime.now() - timedelta(days=1))).where('winner', player['id']).count()
    #return results
    return {'status':'success', 'result':{'id':player['id'], 'name':player['fname'], 'games_today': games, 'wins_today': wins, 'points': player['points']}}