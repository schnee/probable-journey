import argparse
import math
import random
import time
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
        # self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")
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


class Walker:
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
    url = None
    area = None

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
        ("r", "populate_table", "Refresh the Stops"),
        ("g", "go_for_a_walk", "Teleport and Walk"),
    ]

    #   def __init__(self):
    #       super().__init__()
    #       self.walker = Walker(self, interval = 2)

    def compose(self) -> ComposeResult:
        yield DataTable()
        yield TimeDisplay(id="left-bottom")

    def get_row(self):
        table = self.query_one(DataTable)
        row = table.cursor_row
        selected_row = table.get_row_at(row)
        self.log(selected_row)
        return selected_row

    def action_go_for_a_walk(self):
        # new stop - cancel all walking
        self.workers.cancel_group(self, "walk")
        # self.workers.cancel_all()
        row = self.get_row()
        lat = row[2]
        lng = row[3]
        time_display = self.query_one(TimeDisplay)
        time_display.start()
        self.circle_walk(lat, lng)

    @work(exclusive=True, thread=True, group="walk")
    def walk_somewhere(self, lat, lng):
        worker = get_current_worker()
        if not worker.is_cancelled:
            set_location_for_all(lat, lng)
        while not worker.is_cancelled:
            time.sleep(5.0)
            next_point = inverse_haversine(
                (lat, lng), 30, random.uniform(0, 359), Unit.METERS
            )
            if not worker.is_cancelled:
                set_location_for_all(next_point[0], next_point[1])
                time.sleep(5.0)
            if not worker.is_cancelled:
                set_location_for_all(lat, lng)

    @work(exclusive=True, thread=True, group="walk")
    def circle_walk(self, lat, lng):
        worker = get_current_worker()

        # a radius of <= 40 keeps the pokestop of interest in the
        # active zone. Keep the radius constant per stop per loop
        radius = random.uniform(35.0 - 2.5, 35.0 + 2.5)  # meters

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
        stops = get_stops(self.stopType, self.url)
        # Populate table with stops data
        table = self.query_one(DataTable)
        # I do wish I could do this w/o the lambda
        stops.apply(
            lambda row: table.add_row(
                row["row_num"],
                row["name"],
                row["lat"],
                row["lng"],
                row["cool"],
                row["edge_cool"],
                row["distance"],
                row["time_remaining"],
                row["invasion_end"]
            ),
            axis=1,
        )

    def refresh_expirations(self) -> None:
        table = self.query_one(DataTable)
        rows = table.rows
        for row_key in rows:
            log(row_key)
            expiration = table.get_cell(row_key, "invasion_end")
            log(expiration)
            if expiration:  # If there's an expiration time
                current_time = time.time()
                remaining = expiration - current_time
                remaining_seconds = round(remaining)
                edge_cool = table.get_cell(row_key, "edge_cool")
                log(remaining_seconds)
                if remaining_seconds < 0:
                    table.update_cell(row_key, "time_remaining", 
                                      Text(str(remaining_seconds), style="italic #FF0000", justify="right"))
                elif current_time + edge_cool > expiration:
                    table.update_cell(row_key, "time_remaining", 
                                      Text(str(remaining_seconds), style="italic #FFBF00"))
                else:
                    table.update_cell(row_key, "time_remaining", 
                                      remaining_seconds)
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
        table.add_column("ini cd", width=8)
        table.add_column("edge cd", width=8, key="edge_cool")
        table.add_column("dist", width=7)
        table.add_column("remain", width=8, key="time_remaining")
        table.add_column("inv end", width=0, key="invasion_end") # hidden column
        self.action_populate_table()
        self.set_interval(1, self.refresh_expirations, pause=False)


app = JourneyApp()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimal Journey")
    parser.add_argument("-t", "--type", help="the numeric type of the pokestop")
    parser.add_argument("-a", "--area", help="The area you want to explore")
    args = parser.parse_args()

    stopType = int(args.type.strip())

    area = args.area.strip()

    # Read in CSV as DataFrame
    areas_df = pd.read_csv("areas.csv")

    # Lookup url for matching area
    url = areas_df.loc[areas_df["area"] == area, "url"].iloc[0]

    print(f"stop type {stopType} \nurl {url}")

    app.stopType = stopType
    app.url = url
    app.area = area

    app.run()
