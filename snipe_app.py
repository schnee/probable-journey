import argparse
import math
import random
import re
import time
import pyperclip
from textual.widgets import DataTable, Static
from textual.app import App, ComposeResult
from textual.worker import get_current_worker
from textual import work, log
from time import monotonic
from textual.reactive import reactive
import pandas as pd
from optimal_journey import get_stops
from long_march import set_location_for_all
from haversine import inverse_haversine, Unit
from rich.text import Text

def paste_data():
    return pyperclip.paste()
    
def parse_monster_lines(monsters_str):
    """
    Mons should be a string of lines, separated by newlines. Walk throught these lines
    """
    monster_list = monsters_str.split("\n")

    # Remove empty lines
    monster_list = [mon for mon in monster_list if mon]

    # remove each line that does not have ":L_:" in it
    monster_list = [mon for mon in monster_list if ":L_: " in mon]

    df = pd.DataFrame()

    # for each line, extract the values and add those row by row into the list
    levels = []
    lats = []
    lngs = []
    cps = []
    seconds = []
    mon_types = []

    for line in monster_list:
        level = 0
        cp = 0
        lat = 0
        lng = 0
        second = 0
        mon_type = ""
        add_it = True

        match = re.search(r':L_: (\d+)', line)
        if match:
            level = int(match.group(1))

        else:
            add_it = False

        match = re.search(r':C_: (\d+)', line)
        if match:
            cp = int(match.group(1))

        else:
            add_it = False


        # Extract lat and lng
        match = re.search(r'(-?\d+\.\d+),(-?\d+\.\d+)$', line)
        if match:
            lat = float(match.group(1))
            lng = float(match.group(2))

        else:
            add_it = False
            

        # Also extract minutes 
        match = re.search(r'\(:dsp: in (\d+) minutes\)', line)
        if match:
            second = int(match.group(1)) * 60
            
        else:
            add_it = False

        # also extract monster type
        match = re.search(r':(\w+): :(\w+):( :\w+:)? \(:dsp:', line)
        if match:
            mon_type = match.group(1)
        else:
            add_it = False

        # if all the REs matched, then add this row to the list
        if add_it:
            seconds.append(second)
            lats.append(lat)
            lngs.append(lng)
            cps.append(cp)
            levels.append(level)
            mon_types.append(mon_type)


    df = pd.DataFrame(data={'type': mon_types,
                            'seconds': seconds,
                            'level': levels, 
                            'cp': cps,
                            'lat': lats, 
                            'lng': lngs})
    return df

def find_new_monsters(new_df, old_df):
    df3 = pd.merge(new_df, old_df, on=['lat', 'lng', 'level', 'cp'], how='left', indicator=True)
    new_mons = df3[df3['_merge'] == 'left_only'].drop(columns=['_merge', 'seconds_y', 'type_y'])

    new_mons = new_mons.rename(columns={'seconds_x':'seconds'})
    new_mons = new_mons.rename(columns={'type_x': 'type'})
    return new_mons

class SnipeApp(App):

    # keep a dataframe of the mons that had been visited
    visited = pd.DataFrame(data={'seconds': [],
                            'level': [], 
                            'cp': [],
                            'lat': [], 
                            'lng': []})
    CSS = """
    #left-bottom {
            align: left bottom;
        }

    Screen {
            layout: grid;
            grid-size: 1 2;
            grid-rows: 95% 5%;
        }
    
    """

    BINDINGS = [
        ("v", "populate_table", "Refresh the Monsters"),
        ("g", "go_for_a_walk", "Teleport and Walk"),
    ]

    #   def __init__(self):
    #       super().__init__()
    #       self.walker = Walker(self, interval = 2)

    def compose(self) -> ComposeResult:
        yield DataTable()

    def get_row(self):
        table = self.query_one(DataTable)
        row = table.cursor_row
        log("************************")
        log(row)
        selected_row = table.get_row_at(row)
        self.log(selected_row)
        return selected_row

    def action_go_for_a_walk(self):
        # new stop - cancel all walking
        self.workers.cancel_group(self, "walk")
        table = self.query_one(DataTable)
        row = self.get_row()
        lat = row[3]
        lng = row[4]
        self.circle_walk(lat, lng)

    @work(exclusive=True, thread=True, group="walk")
    def circle_walk(self, lat, lng):
        worker = get_current_worker()

        # a radius of <= 40 keeps the pokestop of interest in the
        # active zone. Keep the radius constant per stop per loop
        radius = random.uniform(42.0 - 2.5, 42.0 + 2.5)  # meters

        # get to the first point on the circle
        if not worker.is_cancelled:
            set_location_for_all(lat, lng)
            time.sleep(2.0)
        angle = random.uniform(0, 360)
        next_point = inverse_haversine(
            (lat, lng), radius, math.radians(angle), Unit.METERS
        )
        if not worker.is_cancelled:
            set_location_for_all(next_point[0], next_point[1])
            time.sleep(2.0)
        # walk the circle, by picking a point chord meters from here, but also
        # radius meters from the center (lat, lng). This is accomplished by simply
        # incrementing the angle for the inverse_haversine
        while not worker.is_cancelled:
            # each chord will be a little random, just because humans are a little random

            # want an average speed of X meters per second. If the distance traveled
            # is 35 meters, then the time at that speed should be 35/X seconds.
            # This would be how long to sleep after moving 35 meters "instaneously"
            speed = random.uniform(2.25, 2.75)  # meters per second

            chord = random.uniform(2.2, 2.5)  # meters

            sleep_time = speed / chord  # seconds

            # radius = random.uniform(35.0-2.5, 35.0+2.5) # meters

            # the hypothenus is the radius. The opposite side is one-half the
            # chord. So half the angle is the asin of the ratio of 0.5*chord/radius
            angle_incr = math.degrees(
                math.asin((0.5 * chord) / radius) * 2.0
            )  # in degrees

            angle = angle + angle_incr

            # for every circuit, change the radius a little bit. just because
            if angle > 360:
                radius = random.uniform(35.0 - 2.5, 35.0 + 2.5)  # meters

            angle = angle % 360

            next_point = inverse_haversine(
                (lat, lng), radius, math.radians(angle), Unit.METERS
            )
            if not worker.is_cancelled:
                set_location_for_all(next_point[0], next_point[1])
                time.sleep(sleep_time)

    def clear_table(self):
        table = self.query_one(DataTable)
        table.clear()

    def action_populate_table(self):
        # Get stops data from API
        self.clear_table()
        # Get list of stops
        mons_str = paste_data()
        mons = parse_monster_lines(mons_str)

        # determine which of these stops we haven't visited before
        # we can do this by comparing the lat and lng to the visited stops

        if(len(self.visited) > 0):
            # if we have visited stops, then we can compare the lat and lng
            # to the visited stops

            new_mons = find_new_monsters(mons, self.visited)

            self.visited = pd.concat([self.visited, new_mons]).drop_duplicates(subset=['lat', 'lng', 'level', 'cp'])
            mons = new_mons
        else:
            self.visited = mons


        # Sort the mons by expiration time
        mons = mons.sort_values(by=['seconds'])

        # Populate table with stops data
        table = self.query_one(DataTable)
        # I do wish I could do this w/o the lambda
        mons.apply(
            lambda row: table.add_row(
                Text(text=row["type"]),
                int(row["cp"]),
                int(row["level"]),
                Text(text=str(int(row["seconds"])), justify="right"),
                row["lat"],
                row["lng"],
                row["seconds"], # hidden column for seconds
                row["lat"],     # hidden column for lat
                row["lng"]      # hidden column for lng
            ),
            axis=1,
        )

    def on_mount(self):
        table = self.query_one(DataTable)

        table.border_style = "not rounded"
        table.row_divider = "solid"
        table.header_divider = "solid"
        table.show_header = True
        table.padding = (0, 1)
        table.add_column("type", width=10)
        table.add_column("cp", width=5)
        table.add_column("level", width=5)
        table.add_column(Text("seconds", justify='right'), width = 10)
        table.add_column("lat", width=7)
        table.add_column("lng", width=7),
        # a few hidden columns so that I can directly access the raw values
        table.add_column("seconds_raw", width=0, key="seconds_raw"),
        table.add_column("lat_raw", width=0, key="lat_raw"),
        table.add_column("lng_raw", width=0, key="lng_raw")
        #self.action_populate_table()

app = SnipeApp()
if __name__ == "__main__":

    app.run()
