import foosbot.database as database
from dateutil import parser

#This gets leaderboard data for the pi-based leaderboard. Note that the website leaderboard is loaded in views.py and rendered in template
def get_table_leaderboard(data, account_id):
    db = database.builder('foosbot')
    users = db.table('users').select('id', 'fname', 'lname', 'elo', 'photo').where('account_id', account_id).where_null('deleted_at').order_by('elo', 'desc').limit(100).get()
    data = []
    for i,user in enumerate(users):
        #only show players who have played a game
        has_games = db.table('matches').where('player1', user['id']).or_where('player2', user['id']).exists()
        if not has_games:
            continue
        #add rank
        user['rank'] = len(data)+1
        user['elo'] = int(round(user['elo'])) if user['elo'] else 0
        data.append(user)
        #Limit 20 results
        if len(data) >= 20: break

    return {'status': 'success', 'leaderboard_data':data}

def get_leaderboard(account_id):
    db = database.builder('foosbot')
    players = db.table('users').where('users.account_id', account_id).where_null('deleted_at').order_by('elo', 'desc').get()
    # players = db.table('users').left_join('player_stats', 'users.id','=', 'player_stats.player_id')\
    # .select('users.id', 'users.fname', 'users.elo', 'player_stats.matches', 'users.photo')\
    # .where('users.account_id', account_id).where_null('deleted_at').order_by(db.raw('(matches > 0) desc, elo'), 'desc').get()#).order_by('elo', 'desc').get()
    return players

#return match history and player details
def get_details(account_id, player_id):
    db = database.builder('foosbot')

    player = db.table('users').where('account_id', account_id).where('id', player_id).first()

    matches = db.table('matches').where(
        db.query().where('player1', player['id']).or_where('player2', player['id'])
    )\
    .where('status', 'complete')\
    .select('player1', 'player2', 'winner', 'points', 'created_at')\
    .order_by('created_at', 'desc').get()

    #add names for displaying
    PName = PlayerName()
    longest_streak = 0
    streak = 0
    won = 0
    for match in matches:
        player2 = match.player1 if match.player1 != player['id'] else match.player2
        if match['winner'] == player['id']:
            match['winner_name'] = player['fname']
            match['loser_name'] = PName.getName(player2)
            won += 1
            streak += 1
        else:
            match['winner_name'] = PName.getName(player2)
            match['loser_name'] = player['fname']
            streak = 0

        match['points'] = int(match['points'])
        match['created_at'] = parser.parse(str(match['created_at'])[:11])
        match['created_at'] = match['created_at'].strftime("%b %d")

        if streak > longest_streak: longest_streak = streak
    

    data = {
        'player':player, 
        'matches':matches[:25], 
        'total_played': len(matches), 
        'total_won': won, 
        'win_percent': '%.1f%%'%(100*won/len(matches)), 
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
