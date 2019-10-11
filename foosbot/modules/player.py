import foosbot.database as database

def create_player(player):
    #We need to specify starting ELO before insertion.
    db = database.builder('foosbot')

    #set initial elo
    # player['elo'] = set_starting_elo(player)
    player['elo'] = None

    #strip RFID in case there are spaces
    player['rfid'] = str(player['rfid']).strip()

    #save
    db.table('users').insert(player)

def set_starting_elo(player):
    players = db.table('users').where('account_id', player['account_id']).where_null('deleted_at').where_not_null('elo').get()
    
    #is this the first player?
    if not players or len(players) < 2:
        return 1500    

    #do some math
    import statistics
    elos = [p['elo'] for p in players]
    std = statistics.stdev(elos)
    mean = statistics.mean(elos)

    #start the player at one stdev below the average elo. 
    return mean - std