import argparse
import time
from textual.widgets import DataTable, Static
from textual.app import App, ComposeResult
from textual.keys import Keys
from textual.worker import Worker
from textual import work
from time import monotonic
from textual.reactive import reactive
import pandas as pd
from optimal_journey import get_stops
from long_march import walk, set_location_for_all
from haversine import inverse_haversine, haversine, Unit

class TimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.time = self.total + (monotonic() - self.start_time)

    def watch_time(self, time: float) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        #self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")
        self.update(f" {time:07.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self):
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self):
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0



class Walker():

    def __init__(self, interval):
        self.interval = interval

    def set_initial_lat(self, lat):
        self.lat = lat

    def set_initial_lng(self, lng):
        self.lng = lng

    def set_interval(self, interval):
        self.interval = interval

    @work(exclusive=True)
    async def walk(self):

        set_location_for_all(self.lat, self.lng)
        self.lat += 0.001
        self.lng += 0.001

        await set_location_for_all(self.lat, self.lng)


class JourneyApp(App):

    stopType = None

    BINDINGS = [("r", "populate_table", "Refresh the Stops"),
                ("g", "go_for_a_walk", "Teleport and Walk")]
    
 #   def __init__(self):
 #       super().__init__()
 #       self.walker = Walker(self, interval = 2)

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield TimeDisplay()

    def get_row(self):
        table = self.query_one(DataTable)
        row = table.cursor_row
        selected_row = table.get_row_at(row)
        self.log(selected_row)
        return selected_row

    @work(exclusive=True, thread=True)
    async def action_go_for_a_walk(self):
        walker = Walker(self)
        row = self.get_row()
        lat = row[2]
        lng = row[3]
        time_display = self.query_one(TimeDisplay)
        time_display.start()
        set_location_for_all(lat, lng)
        time.sleep(5.0)
        next_point = inverse_haversine((lat, lng), 10, 45, Unit.METERS)
        set_location_for_all(next_point[0], next_point[1])  
        # walker.set_interval(2.0)
        # walker.set_initial_lat(lat)
        # walker.set_initial_lng(lng)
        # walker.walk()

    def clear_table(self):
        table = self.query_one(DataTable)
        table.clear()

    def action_populate_table(self):
        # Get stops data from API
        self.clear_table()
        # Get list of stops
        stops = get_stops(self.stopType)
        # Populate table with stops data
        table = self.query_one(DataTable)
        # I do wish I could do this w/o the lambda
        stops.apply(lambda row: 
              table.add_row(row['row_num'],row['name'],row['lat'],row['lng'],
                            row['cool'],row['edge_cool'],row['distance'],row['invasion_end']), axis=1)

    def on_mount(self):
        table = self.query_one(DataTable)
       
        table.border_style = "not rounded"
        table.row_divider = "solid"
        table.header_divider = "solid"
        table.show_header = True
        table.padding = (0, 1)

        table.add_column("rn", width=3)
        table.add_column("name", width=10)
        table.add_column("lat", width=6)
        table.add_column("lng", width=6)
        table.add_column("ini cd", width=9)
        table.add_column("edge cd", width=9)
        table.add_column("dist", width=8)
        table.add_column("inv end", width=9)
        self.action_populate_table()

app = JourneyApp()
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'Optimal Journey')
    parser.add_argument('-t', '--type', help='the numeric type of the pokestop')
    args = parser.parse_args()

    stopType = int(args.type.strip())

    app.stopType = stopType

    app.run()