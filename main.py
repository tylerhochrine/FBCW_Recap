from yahoo_fantasy_api import Game, League
from yahoo_oauth import OAuth2
from datetime import timedelta
import functions as func
import data_storage as ds

SEASON_WEEK = 8

oauth = OAuth2(None, None, from_file='oauth2.json')
league_id = '431.l.8434'
gm = Game(oauth, 'mlb')
lg = League(oauth, league_id)

week_range = lg.week_date_range(SEASON_WEEK)
start_date, end_date = week_range[0], week_range[1] + timedelta(days=1)
players = lg.taken_players() + lg.free_agents('B') + lg.free_agents('P')
player_ids = []
batter_weekly_stats, pitcher_weekly_stats = [], []
highest_scoring_appearance = ['',0]
lowest_scoring_appearance = ['',0]
daily_stats = []
day_of_week = 0

for player in players:
    player_ids.append(player['player_id'])

if not ds.data_exists(SEASON_WEEK, day_of_week):
    daily_stats = lg.player_stats(player_ids, 'date', date=start_date)
    for player in daily_stats:
        player['fantasy_points'] = func.calculate_fantasy_points(player['position_type'], player)
    ds.store_data(daily_stats, SEASON_WEEK, day_of_week)
else:
    daily_stats = ds.get_data(SEASON_WEEK, day_of_week)

for player in daily_stats:
    if player['position_type'] == 'B':
        batter_weekly_stats.append(player)
    elif player['position_type'] == 'P':
        pitcher_weekly_stats.append(player)
        highest_scoring_appearance, lowest_scoring_appearance = func.best_and_worst_start(highest_scoring_appearance, lowest_scoring_appearance, player)

day_of_week += 1

start_date = start_date + timedelta(days=1)

for day in func.daterange(start_date, end_date):
    batter_day_stats, pitcher_day_stats = [], []
    if not ds.data_exists(SEASON_WEEK, day_of_week):
        daily_stats = lg.player_stats(player_ids, 'date', date=day)
        for player in daily_stats:
            player['fantasy_points'] = func.calculate_fantasy_points(player['position_type'], player)
        ds.store_data(daily_stats, SEASON_WEEK, day_of_week)
    else:
        daily_stats = ds.get_data(SEASON_WEEK, day_of_week)

    for player in daily_stats:
        if player['position_type'] == 'B':
            batter_day_stats.append(player)
        elif player['position_type'] == 'P':
            pitcher_day_stats.append(player)
            highest_scoring_appearance, lowest_scoring_appearance = func.best_and_worst_start(highest_scoring_appearance, lowest_scoring_appearance, player)
    day_of_week += 1
    
    for idx, player in enumerate(batter_day_stats):
        batter_weekly_stats[idx] = func.merge_stats('B', batter_weekly_stats[idx], batter_day_stats[idx])
    for idx, player in enumerate(pitcher_day_stats):
        pitcher_weekly_stats[idx] = func.merge_stats('P', pitcher_weekly_stats[idx], pitcher_day_stats[idx])

day_of_week = 1

for day in func.daterange(start_date, end_date):
    daily_stats = ds.get_data(SEASON_WEEK, day_of_week)
    for player in batter_weekly_stats:
        player['fantasy_points'] += func.find_player_points(player['player_id'], daily_stats)
        player['fantasy_points'] = round(player['fantasy_points'], 1)
    for player in pitcher_weekly_stats:
        player['fantasy_points'] += func.find_player_points(player['player_id'], daily_stats)
        player['fantasy_points'] = round(player['fantasy_points'], 2)
    
    day_of_week += 1

print('Week ' + str(SEASON_WEEK) + ' Recap!' + '\n')
func.print_stat_leaders('fantasy_points', pitcher_weekly_stats, 'Top Pitchers', medals=['🥇','🥈','🥉'])
func.print_appearance_of_the_week(highest_scoring_appearance, 'Start of the Week 💪🏻')
func.print_appearance_of_the_week(lowest_scoring_appearance, 'Fart of the Week 😷')
func.print_stat_leaders('K', pitcher_weekly_stats, 'K King 👑', n=1)
func.print_stat_leaders('IP', pitcher_weekly_stats, 'Inning Eater 🍽️', n=1)
func.print_stat_leaders('SV', pitcher_weekly_stats, 'Save King 👑', n=1)
func.print_stat_leaders('fantasy_points', batter_weekly_stats, 'Top Hitters', medals=['🥇','🥈','🥉'])
func.print_stat_leaders('fantasy_points', batter_weekly_stats, 'Bottom Batter 🚮', best_stats=False, n=1)
func.print_stat_leaders('HR', batter_weekly_stats, 'HR King 👑', n=1)
func.print_stat_leaders('TB', batter_weekly_stats, 'Biggest Bagger 💯', n=1)
func.print_stat_leaders('SB', batter_weekly_stats, 'Speed Demon 💨', n=1)
