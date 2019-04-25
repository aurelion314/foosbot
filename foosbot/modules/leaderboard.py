import foosbot.database as database

#return match history and player details
def get_details(client_id, player_id):
    db = database.builder('foosbot')

    player = db.table('users').where('client_id', client_id).where('id', player_id).first()

    matches = db.table('matches').where(
        db.query().where('player1', player['id']).or_where('player2', player['id'])
    ).order_by('created_at', 'desc').limit(25).get()

    #add names for displaying
    pname = PlayerName()
    for match in matches:
        player2 = match.player1 if match.player1 != player['id'] else match.player2
        if match['winner'] == player['id']:
            match['winner_name'] = player['fname']
            match['loser_name'] = pname.getName(player2)
        else:
            match['winner_name'] = pname.getName(player2)
            match['loser_name'] = player['fname']
        match['delta_elo'] = int(match['delta_elo'])
        match['created_at'] = match['created_at'][:11]
    

    data = {
        'player':player, 
        'matches':matches, 
        'total_played': 10, 
        'total_won': 9, 
        'longest_streak': 5,
        'client_id':client_id
    }

    return data

class PlayerName():
    def __init__(self):
        self.players = {}
    
    def getName(self, player_id):
        #have we checked for this id before?
        if id not in self.players:
            #nope, so find it from DB
            db = database.builder('foosbot')
            player = db.table('users').where('id', player_id).select('id', 'fname').first()
            if not player: return None
            
            #cache it for later
            self.players[player['id']] = player['fname']

            return player['fname']
        else:
            #returned the cached name
            return self.players[player_id]

if __name__ == "__main__":
    np = PlayerName()
    print(np.getName(2))
