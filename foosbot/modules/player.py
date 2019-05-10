import foosbot.database as database

def create_player(player):
    #We need to specify starting ELO before insertion.
    db = database.builder('foosbot')

    players = db.table('users').where('account_id', player['account_id']).where_null('deleted_at').where_not_null('elo').get()
    
    #is this the first player?
    if not players:
        player['elo'] = 1500    
        db.table('users').insert(player)
        return True

    #do some math
    import statistics
    elos = [p['elo'] for p in players]
    std = statistics.stdev(elos)
    mean = statistics.mean(elos)

    #start the player at one stdev below the average elo. 
    player['elo'] = mean - std

    #save
    db.table('users').insert(player)
