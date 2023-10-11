import pandas as pd

def get_cooldown():
    df_cool = pd.read_csv("cooldown.csv")
    return df_cool.sort_values(by='distance')

# returns the cooldown time for a given distance
def cooldown(dist, df_cool):
     
    #subset df_cool to just the values >= dist
    df = df_cool[df_cool['distance'] >= dist]

    #print(df)

    # these are in minutes; convert to seconds
    return df.iat[0,1] * 60