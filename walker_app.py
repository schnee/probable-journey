import math
import random
from textual.widgets import Static, Digits, Switch
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.containers import Horizontal
from optimal_journey import get_lastloc
from long_march import set_location_for_all
from haversine import inverse_haversine, Unit


class Velocity(Digits):
    bearing = reactive(0.0)
    speed = reactive(0.0)

    def turn(self, delta: float):
        self.bearing = (self.bearing + delta) % 360

    def accelerate(self, delta: float):
        self.speed += delta
        if self.speed > 2.7:
            self.speed = 2.7
        elif self.speed < 0.0:
            self.speed = 0.0

    def stop(self):
        self.speed = 0.0

    def watch_bearing(self, bearing: float) -> None:
        self.update(f"{self.speed:03.2f} : {self.bearing:03.0f}")

    def watch_speed(self, speed: float) -> None:
        self.update(f"{self.speed:03.2f} : {self.bearing:03.0f}")


class WalkerApp(App):

    action_sw = Switch(id="action_sw", value=True)

    CSS = """
Screen {
    align: center middle;
}

.container {
    height: auto;
    width: auto;
}

Switch {
    height: auto;
    width: auto;
}

.label {
    height: 3;
    content-align: center middle;
    width: auto;
}

#custom-design {
    background: darkslategrey;
}

#custom-design > .switch--slider {
    color: dodgerblue;
    background: darkslateblue;
}
"""

    BINDINGS = [
        ("s", "turn_left", "left turn"),
        ("f", "turn_right", "right turn"),
        ("e", "faster", "faster"),
        ("d", "slower", "slower"),
        ("c", "stop", "stop"),
        ("g", "fine_right", "small right"),
        ("a", "fine_left", "small_left")
    ]

    def on_mount(self) -> None:
        self.interval_timer = self.set_interval(1, self.move)
        self.is_paused = False

    def compose(self) -> ComposeResult:
        yield Velocity()

        yield Horizontal(
            Static("Active: ", classes="label"), self.action_sw, classes="container"
        )

    def on_switch_changed(self, switch: Switch) -> None:
        if switch.value:
            self.interval_timer.resume()
        else:
            self.interval_timer.pause()

    def action_fine_right(self):
        bd = self.query_one(Velocity)
        bd.turn(5)

    def action_fine_left(self):
        bd = self.query_one(Velocity)
        bd.turn(-5)

    def action_turn_left(self):
        bd = self.query_one(Velocity)
        bd.turn(-15)

    def action_turn_right(self):
        bd = self.query_one(Velocity)
        bd.turn(15)

    def action_faster(self):
        vel = self.query_one(Velocity)
        vel.accelerate(0.1)

    def action_slower(self):
        vel = self.query_one(Velocity)
        vel.accelerate(-0.1)

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
            last_lat = df_lastloc.at[0, "lat"]
            last_lng = df_lastloc.at[0, "lng"]
            next_point = inverse_haversine(
                (last_lat, last_lng),
                vel.speed + offset,
                math.radians(vel.bearing),
                Unit.METERS,
            )
            set_location_for_all(next_point[0], next_point[1])


if __name__ == "__main__":
    app = WalkerApp()
    app.run()
