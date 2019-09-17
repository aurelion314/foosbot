import foosbot.database as database
from datetime import datetime, timedelta
from foosbot.modules.slack import Slack

MAX_POINTS_GAIN = 40

def end(data, account_id):
    db = database.builder('foosbot')    

    #validate
    if 'winner' not in data: return {'status': 'no winner given'}
    winner = data['winner']
    loser = data['player1'] if winner!=data['player1'] else data['player2']
    
    #load the players
    winner = db.table('users').where('id', winner).first()
    loser = db.table('users').where('id', loser).first()

    #ensure there is a match in progress
    match = db.table('matches').select('id').where('account_id', account_id).where('player1', data['player1']).where('player2', data['player2']).where('status', 'in_progress').lock_for_update().first()
    if not match: return {'status': 'no match found'}

    #find winning player streak
    streak = 1
    games = db.table('matches').where(
        db.query().where('player1', winner['id']).or_where('player2', winner['id'])
    ) \
    .where('status', 'complete').order_by('created_at', 'desc').get()

    for game in games:
        if game['winner'] != winner['id']: break
        streak += 1
    
    #calculate the ELO change
    elo_change = calculate_elo_change(winner['elo'], loser['elo'])
    elo_won, elo_lost = get_real_elo_change(elo_change, account_id)
    # points_won, points_lost = get_points_change(winner, loser, elo_won, elo_lost)

    # print(elo_change, elo_won, elo_lost, points_won, points_lost)

    #update the match
    db.table('matches').where('player1', data['player1']).where('player2', data['player2']).where('status', 'in_progress') \
        .update({'status': 'complete', 'winner':data['winner'], 'updated_at':str(datetime.now()), 'points': elo_change})

    db.table('users').where('id', winner['id']).update({'elo': winner['elo'] + elo_won}) #'points':winner['points'] + points_won
    db.table('users').where('id', loser['id']).update({'elo': loser['elo'] - elo_lost}) #'points':loser['points'] - points_lost

    #update slack if applicable
    Slack.end_match(match['id'], winner, loser, streak, int(elo_change))

    #return results
    return {'status': 'success', 'streak':streak, 'points':int(elo_change)}

#We want them to be the same after a while, so even them out here.
def get_points_change(winner, loser, elo_won, elo_lost):
    #Winning. If elo is higher, gain extra points up to max of 50
    if winner['elo'] > winner['points']:
        points_missing = winner['elo'] - winner['points']
        if points_missing + elo_won > MAX_POINTS_GAIN:
            points_won = MAX_POINTS_GAIN
        else:
            points_won = points_missing + elo_won
    else:
        points_won = elo_won


    #Losing. if points is lower, lose less points to normalize. 
    if loser['points'] < loser['elo']:
        #Points is too low. don't lose as much
        points_missing = loser['elo'] - loser['points']
        if points_missing > elo_lost:
            points_lost = 0
        else:
            points_lost = elo_lost - points_missing
    elif loser['points'] > loser['elo']:
        #points too high. lose extra
        points_surplus = loser['points'] - loser['elo']
        if points_surplus + elo_lost > MAX_POINTS_GAIN:
            points_lost = MAX_POINTS_GAIN
        else:
            points_lost = elo_lost + points_surplus
    else:
        points_lost = elo_lost

    return points_won, points_lost


#Alter the real change in Elo to keep the average elo near 1500
def get_real_elo_change(elo_change, account_id):
    if elo_change < 5: return [elo_change, elo_change]
    db = database.builder('foosbot') 

    elo_average = db.table('users').where('account_id', account_id).where_null('deleted_at').select(db.raw('avg(elo) as average_elo')).first()['average_elo']
    print('elo average', elo_average)
    if elo_average >1525:
        return [elo_change-1, elo_change+1] #win less, lose more
    if elo_average <1475:
        return [elo_change+1, elo_change-1] #win more, lose less
    
    return [elo_change, elo_change]

def calculate_elo_change(elo1, elo2):
    max_change = MAX_POINTS_GAIN 
    win_probability = calculate_win_probability(elo1, elo2)
    return (max_change*(1-win_probability))

def calculate_win_probability(elo1, elo2):
    return 1/(1+10**((elo2-elo1) / 400))