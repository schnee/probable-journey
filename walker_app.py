import math
import random
from textual.widgets import Static,Digits
from textual.app import App, ComposeResult
from textual.reactive import reactive
from optimal_journey import get_lastloc
from long_march import set_location_for_all
from haversine import inverse_haversine, Unit

class Velocity(Digits):
    bearing = reactive(0.0)
    speed = reactive(0.0)  

    def left(self):
        self.bearing = (self.bearing - 15.0) % 360

    def right(self):
        self.bearing = (self.bearing + 15.0) % 360

    def faster(self):
        self.speed += 0.1
        if self.speed > 2.7:
            self.speed = 2.7

    def slower(self):
        self.speed -= 0.1
        if self.speed < 0.0:
            self.speed = 0.0

    def stop(self):
        self.speed = 0.0

    def watch_bearing(self, bearing: float) -> None:
        self.update(f"{self.speed:03.2f} : {self.bearing:03.0f}")

    def watch_speed(self, speed: float) -> None:
        self.update(f"{self.speed:03.2f} : {self.bearing:03.0f}")


class WalkerApp(App):


    BINDINGS = [("s", "turn_left", "left turn"),
                ("f", "turn_right", "right turn"),
                ("e", "faster", "faster"),
                ("d", "slower", "slower"),
                ("c", "stop", "stop")]
    

    def on_mount(self) -> None:
        self.set_interval(1, self.move)

    def compose(self) -> ComposeResult:
        yield Velocity()

    def action_turn_left(self):
        bd = self.query_one(Velocity)
        bd.left()

    def action_turn_right(self):
        bd = self.query_one(Velocity)
        bd.right()

    def action_faster(self):
        vel = self.query_one(Velocity)
        vel.faster()
    
    def action_slower(self):
        vel = self.query_one(Velocity)
        vel.slower()

    def action_stop(self):
        vel = self.query_one(Velocity)
        vel.stop()

    def move(self) -> None:
        vel = self.query_one(Velocity)
        offset = 0
        if vel.speed > 0:
            if vel.speed >= 1.5:
                offset = random.uniform(-0.125, 0.125)
            df_lastloc = get_lastloc()
            last_lat = df_lastloc.at[0,'lat']
            last_lng = df_lastloc.at[0,'lng']
            next_point = inverse_haversine((last_lat, last_lng), vel.speed + offset, math.radians(vel.bearing), Unit.METERS)
            set_location_for_all(next_point[0], next_point[1]) 
   
if __name__ == "__main__":

    app = WalkerApp()
    app.run()