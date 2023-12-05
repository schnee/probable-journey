import math
from textual.widgets import Static,Digits
from textual.app import App, ComposeResult
from textual.reactive import reactive
from optimal_journey import get_lastloc
from long_march import set_location_for_all
from haversine import inverse_haversine, Unit

class BearingDisplay(Digits):
    bearing = reactive(0.0)

    def left(self):
        self.bearing = (self.bearing - 15.0) % 360

    def right(self):
        self.bearing = (self.bearing + 15.0) % 360

    def watch_bearing(self, bearing: float) -> None:
        self.update(f"{bearing:02.0f}")


class WalkerApp(App):

    speed = 0.0

    BINDINGS = [("s", "turn_left", "left turn"),
                ("f", "turn_right", "right turn"),
                ("e", "forward", "forward")]
    


    def compose(self) -> ComposeResult:
        yield BearingDisplay()

    def action_turn_left(self):
        bd = self.query_one(BearingDisplay)
        bd.left()

    def action_turn_right(self):
        bd = self.query_one(BearingDisplay)
        bd.right()

    def action_forward(self):
        bd = self.query_one(BearingDisplay)
        df_lastloc = get_lastloc()
        last_lat = df_lastloc.at[0,'lat']
        last_lng = df_lastloc.at[0,'lng']
        next_point = inverse_haversine((last_lat, last_lng), 5, math.radians(bd.bearing), Unit.METERS)

        set_location_for_all(next_point[0], next_point[1]) 
   
   
if __name__ == "__main__":

    app = WalkerApp()
    app.run()