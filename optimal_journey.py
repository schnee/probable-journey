import argparse
import requests
import utils
from haversine import haversine, Unit
import pandas as pd 
from textual.app import App
from stop_analytics import reorder_stops

###
#var males = [4, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39];
#var females = [5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38];

#var gruntDict = {4:"grunt",5:"grunt",6:"bug",7:"bug",48:"ghost",47:"ghost",10:"dark",
# 11:"dark",12:"dragon",13:"dragon",14:"fairy",15:"fairy",16:"fighting",17:"fighting",
# 18:"fire",19:"fire",20:"flying",21:"flying",22:"grass",23:"grass",24:"ground",
# 25:"ground",26:"ice",27:"ice",28:"metal",29:"metal",30:"normal",31:"normal",
# 32:"poison",33:"poison",34:"psychic",35:"psychic",36:"rock",37:"rock",38:"water",
# 39:"water",49:"electric",50:"electric",41:"cliff",42:"arlo",43:"sierra",
# 44:"giovanni",500: "npc",501: "npc",502: "npc",503: "npc",504: "npc",505: "npc",
# 506: "npc",507: "npc",508: "npc",509: "npc",510: "npc", 9999:"kecleon", 
# 9998:"gimmighoul_coin", 9997:"showcase"};
###



def get_invasions():
    r = requests.get('https://nycpokemap.com/pokestop.php')
    data = r.json()
    return data

def get_lastloc(): 
    df_loc = pd.read_csv("last_loc.csv")
    return df_loc



def get_stops(stopType):
    
    df_lastloc = get_lastloc()
    last_lat = df_lastloc.at[0,'lat']
    last_lng = df_lastloc.at[0,'lng']
    print(last_lat, last_lng)

    df_cool = utils.get_cooldown()

    data = get_invasions()
    df = pd.json_normalize(data['invasions'])

    df_request_time = pd.json_normalize(data['meta'])
    #print(df_request_time)
    rtime = df_request_time.iloc[0,0]


    # adjust invasion_end to be relative to when the request was made
    df['invasion_end'] = df['invasion_end'] - rtime

    print(df)

    # filter to just the invasions of interest
    df2 = df[df['character'] == stopType].reset_index(drop=True)
    print(df2)

    # now the main logic. first, calculate the distance to each 
    # invasion from the last location.

    df2.loc[:,'distance'] = df2.apply(lambda row : haversine((row['lat'],
                     row['lng']), (last_lat, last_lng)), axis = 1)
    

    
    # next, calculate the cooldown time in seconds for each
    # invasion, based on the distance. 
    df2.loc[:,'cool'] = df2.apply(lambda row: 
                                  utils.cooldown(row['distance'], df_cool), 
                                  axis = 1 )
    
    # Add row number column 
    df2['row_num'] = df2.reset_index().index

    # ok, now, subset so that we have only those invasions that we can get to
    # before they expire. current_time + cool < expiration...

    df2 = df2[(df2['cool']) < df2['invasion_end']].sort_values(by='distance')

    # Sort by distance
    df2 = df2.sort_values('distance') 

    # Keep first 20 rows
    df2 = df2.iloc[:20]

    stops = reorder_stops(df2, df_cool)

    return stops

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Optimal Journey')
    parser.add_argument('-t', '--type', help='the numeric type of the pokestop')
    args = parser.parse_args()

    stopType = int(args.type.strip())
       
    print(f'stop type {stopType}')

    df2 = get_stops(stopType)

    print(df2)

    df2.apply(lambda row: 
              print(f"{row['row_num']} {row['lat']},{row['lng']} {row['cool']} {row['name']}"), 
              axis =1 )

    

