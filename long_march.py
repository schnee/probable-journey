import argparse
import concurrent.futures
import random
import math
import time

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.simulate_location import DtSimulateLocation
from pymobiledevice3.usbmux import list_devices
from datetime import timedelta
from haversine import inverse_haversine, haversine, Unit
from itertools import repeat

# Parse command line arguments
parser = argparse.ArgumentParser(description='Accept two comma-separated numbers')
parser.add_argument('-s', '--secs', metavar='N', default=100, type=int,
                    help='approx number of seconds to walk out before turning around')
parser.add_argument('-m','--mps', metavar='M', default=3, type=float,
                    help='approx meters per second to walk')
parser.add_argument('nums', metavar='num1,num2', type=str,
                    help='two comma-separated numbers')
args = parser.parse_args()

num1_str, num2_str = args.nums.split(",")
latitude = float(num1_str.strip())
longitude = float(num2_str.strip())
seconds_to_walk = args.secs
meters_per_step_base = args.mps

print(f"lat = {latitude}, lng = {longitude}")
print(f"secs = {seconds_to_walk}")
print(f"meters per second = {meters_per_step_base}")

the_devices = list_devices()


# image_mounter = MobileImageMounterService(lockdown=device_lockdown_client)
# image = '/home/brent/projects/Xcode_Developer_Disk_Images/Developer Disk Image/15.7/DeveloperDiskImage.dmg'
# signature = image + '.signature'
#
# image = Path(image).read_bytes()
# signature = Path(signature).read_bytes()

# image_mounter.upload_image('Developer', image, signature)
# image_mounter.mount('Developer', signature)

# the sleep time is set to 1 second, so that we're moving meters_per_step / second.

def set_location(devices, lat, lng):
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
        e.map(set_loc, devices, repeat(lat), repeat(lng))
    #time.sleep(0.45)


def set_loc(device, lat, lng):
    device_lockdown_client = LockdownClient(device.serial)
    location_simulator = DtSimulateLocation(lockdown=device_lockdown_client)
    location_simulator.set(lat, lng)


set_location(the_devices, latitude, longitude)

start = time.time()
now = start
target_dur: float = 2 * 60 * 60  # two * 60 minutes/hour * 60 seconds/minute
elapsed = 0

step_range = meters_per_step_base * 0.1
next_point = (latitude, longitude) # initialize
start_point = next_point
current_point = start_point
total_distance = 0


# Walk 'meters_per_step' in the 'step_direction' until target_dur is exceeded. First head one way out
# and then head the opposite direction back
while elapsed < target_dur:
    current = time.time()
    elapsed = current - start
    print(timedelta(seconds=round(elapsed)), round(total_distance,2), round(total_distance/elapsed,2))
    step_direction = math.radians(random.uniform(0, 360))  # because why not
    start_point = next_point
    for direction in (step_direction, step_direction - math.pi):
        for i in range(seconds_to_walk):
            loop_start = time.time()
            prior_point = current_point
            current_point = next_point
            set_location(the_devices, current_point[0], current_point[1])
            distance = haversine(prior_point, current_point, unit=Unit.METERS)
            total_distance += distance
            meters_per_step = random.uniform(meters_per_step_base-step_range, meters_per_step_base+step_range)
            next_point = inverse_haversine(current_point, meters_per_step, direction, Unit.METERS)
            loop_elapsed = time.time() - loop_start
            if loop_elapsed < 1:
                time.sleep(1 - loop_elapsed)
        current = time.time()
        elapsed = current - start
        print(timedelta(seconds=round(elapsed)), round(total_distance, 2), round(total_distance / elapsed, 2))