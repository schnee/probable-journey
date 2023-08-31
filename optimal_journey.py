import requests
from haversine import haversine, Unit
import pandas as pd    


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

if __name__ == '__main__':
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
    df2 = df[df['character'] == 12].reset_index(drop=True)
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

    df2.apply(lambda row: 
              print(f"{row['lat']},{row['lng']} {row['cool']} {row['name']}"), 
              axis =1 )

    

