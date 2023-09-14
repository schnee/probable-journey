import argparse
import requests
from haversine import haversine, Unit
import pandas as pd 
from textual.app import App

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

def get_cooldown():
    df_cool = pd.read_csv("cooldown.csv")
    return df_cool.sort_values(by='distance')

def cooldown(dist, df_cool):
     
    #subset df_cool to just the values >= dist
    df = df_cool[df_cool['distance'] >= dist]

    #print(df)

    return df.iat[0,1]

def get_stops(stopType):
    
    df_lastloc = get_lastloc()
    last_lat = df_lastloc.at[0,'lat']
    last_lng = df_lastloc.at[0,'lng']
    print(last_lat, last_lng)

    df_cool = get_cooldown()

    data = get_invasions()
    df = pd.json_normalize(data['invasions'])

    df_request_time = pd.json_normalize(data['meta'])
    #print(df_request_time)
    rtime = df_request_time.iloc[0,0]


    # filter to just the invasions of interest
    df2 = df[df['character'] == stopType].reset_index(drop=True)
    #print(df2)

    # now the main logic. first, calculate the distance to each 
    # invasion from the last location.

    df2.loc[:,'distance'] = df2.apply(lambda row : haversine((row['lat'],
                     row['lng']), (last_lat, last_lng)), axis = 1)
    

    
    # next, calculate the cooldown time in seconds for each
    # invasion, based on the distance. To get seconds, multiply
    # by 60.

    df2.loc[:,'cool'] = df2.apply(lambda row: 
                                  cooldown(row['distance'], df_cool) *60, 
                                  axis = 1 )

    # ok, now, subset so that we have only those invasions that we can get to
    # before they expire. current_time + cool < expiration...

    df2 = df2[(rtime+df2['cool']) < df2['invasion_end']].sort_values(by='distance')
    return df2

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description = 'Optimal Journey')
    parser.add_argument('-t', '--type', help='the numeric type of the pokestop')
    args = parser.parse_args()

    stopType = int(args.type.strip())
       
    print(f'stop type {stopType}')

    df2 = get_stops(stopType)

    df2.apply(lambda row: 
              print(f" {row['lat']},{row['lng']} {row['cool']} {row['name']}"), 
              axis =1 )

    

