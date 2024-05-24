from datetime import timedelta
from operator import itemgetter

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

def normalize_innings_pitched(innings):
    if innings != '-': 
            innings = str(round(float(innings), 1)).split('.')
            full_inn, partial_inn = int(innings[0]), int(innings[1])
            full_inn += int(partial_inn / 3)
            partial_inn %= 3
            innings = round(float(str(full_inn) + '.' + str(partial_inn)), 1)
    return innings

def calculate_innings_pitched(innings, points_per):
    total = 0.0
    innings = str(innings).split('.')
    full_innings, partial_innings = int(innings[0]), int(innings[1])
    total += full_innings * points_per
    match partial_innings:
        case 1:
            total += points_per / 3
        case 2:
            total += points_per / 3 * 2       

    return total

def calculate_fantasy_points(position_type, player_stats):
    batter_stat_cats = [['1B',1.1],['2B',2.2],['3B',3.3],['HR',4.4],['RBI',1],['SB',2],['CS',-1],['BB',1],['IBB',1],['HBP',1],['K',-0.5],['CYC',5],['SLAM',2]]
    pitcher_stat_cats = [['IP',2.5],['W',2.5],['L',-3],['CG',5],['SHO',5],['SV',5],['H',-0.75],['ER',-1.75],['BB',-0.75],['K',1.5],['HLD',2],['PICK',3],['NH',10],['QS',3]]
    points = 0.0
    match position_type:
        case 'B':
            for category in batter_stat_cats:
                if player_stats[category[0]] != '-':
                    points += player_stats[category[0]] * category[1]
            points = round(points, 1)
        case 'P':
            for category in pitcher_stat_cats:
                if player_stats[category[0]] != '-':
                    if category[0] == 'IP':
                        points += calculate_innings_pitched(player_stats['IP'], category[1])
                    else:
                        points += player_stats[category[0]] * category[1]
            points = round(points, 2)
    return points

def merge_stats(position_type, player_stats, new_stats):
    batter_stat_cats = ['G','GS','AB','R','H','1B','2B','3B','HR','RBI','SB','CS','BB','IBB','HBP','K','GDP','TB','CYC','PA','SLAM']
    pitcher_stat_cats = ['G','GS','IP','W','L','CG','SHO','SV','H','BF','R','ER','HR','BB','IBB','HBP','K','BK','WP','HLD','PICK','NH','QS','BS','NSV']
    match position_type:
        case 'B':
            for category in batter_stat_cats:
                if player_stats[category] == '-':
                    player_stats[category] = new_stats[category]
                elif new_stats[category] == '-':
                    continue
                else:
                    player_stats[category] += new_stats[category]
        case 'P':
            for category in pitcher_stat_cats:
                if player_stats[category] == '-':
                    player_stats[category] = new_stats[category]
                elif new_stats[category] == '-':
                    continue
                else:
                    player_stats[category] += new_stats[category]
            
            normalize_innings_pitched(player_stats['IP']) 

    return player_stats

def stat_leaders(category, weekly_stats, best_stats=True):
    stat_list = []
    for player in weekly_stats:
        if player[category] != '-':
            stat_list.append([player['name'], player[category]])
    
    stat_list = sorted(stat_list, key=itemgetter(1), reverse=best_stats)

    print(category + ':')
    for i in range(10):
        print(i+1, ':', stat_list[i][0], ',', str(stat_list[i][1]))
    print('\n')

def best_and_worst_start(highest_scoring_start, lowest_scoring_appearance, player):
    if player['IP'] != '-':
        appearance_score = calculate_fantasy_points('P', player)
        if appearance_score > highest_scoring_start[1]:
            highest_scoring_start = [player['name'], appearance_score]
        elif appearance_score < lowest_scoring_appearance[1]:
            lowest_scoring_appearance = [player['name'], appearance_score]

    return highest_scoring_start, lowest_scoring_appearance

def find_player_points(player_id, daily_stats):
    for player in daily_stats:
        if player_id == player['player_id']:
            return player['fantasy_points']
