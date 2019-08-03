import foosbot.database as database
from dateutil import parser

#This gets leaderboard data for the pi-based leaderboard. Note that the website leaderboard is loaded in views.py and rendered in template
def get_leaderboard(data, account_id):
    db = database.builder('foosbot')
    users = db.table('users').where('account_id', account_id).where_null('deleted_at').order_by('elo', 'desc').limit(10).get()
    data = []
    for i,user in enumerate(users):
        has_games = db.table('matches').where('player1', user['id']).or_where('player2', user['id']).exists()
        if not has_games:
            continue
        user['rank'] = i+1
        user['elo'] = int(user['elo'])
        data.append(user)

    return {'status': 'success', 'leaderboard_data':data}

#return match history and player details
def get_details(account_id, player_id):
    db = database.builder('foosbot')

    player = db.table('users').where('account_id', account_id).where('id', player_id).first()

    matches = db.table('matches').where(
        db.query().where('player1', player['id']).or_where('player2', player['id'])
    )\
    .where('status', 'complete')\
    .order_by('created_at', 'desc').limit(25).get()

    #add names for displaying
    pname = PlayerName()
    longest_streak = 0
    streak = 0
    for match in matches:
        player2 = match.player1 if match.player1 != player['id'] else match.player2
        if match['winner'] == player['id']:
            match['winner_name'] = player['fname']
            match['loser_name'] = pname.getName(player2)
            streak += 1
        else:
            match['winner_name'] = pname.getName(player2)
            match['loser_name'] = player['fname']
            streak = 0

        match['points'] = int(match['points'])
        match['created_at'] = parser.parse(str(match['created_at'])[:11])
        match['created_at'] = match['created_at'].strftime("%b %d")

        if streak > longest_streak: longest_streak = streak
    

    data = {
        'player':player, 
        'matches':matches, 
        'total_played': len(matches), 
        'total_won': len([m for m in matches if m['winner']==player['id']]), 
        'longest_streak': longest_streak,
        'account_id':account_id
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
