import argparse
import concurrent.futures
import csv
import random
import math
import time

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.simulate_location import DtSimulateLocation
from pymobiledevice3.usbmux import list_devices
from datetime import timedelta
from haversine import inverse_haversine, haversine, Unit
from itertools import repeat
from urllib.parse import urlparse
from urllib.parse import parse_qs

def get_latlng(url):
    o = urlparse(url)
    if o.scheme:
        qdict = parse_qs(o.query)
        latlng = qdict.get('q')[0]
    else:
        latlng = url
    return latlng

def dist_from_last(lat, lng):
    last_lat = 0
    last_lng = 0
    with open("last_loc.csv", mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            last_lat = float(row['lat'])
            last_lng = float(row['lng'])
    distance = haversine((lat,lng),(last_lat,last_lng)) # kilometers
    return distance

def cooldown(dist):
    with open("cooldown.csv", 'r') as file:
        # Create a DictReader object
        csv2dict = csv.DictReader(file)

        # Convert the CSV file into a dictionary
        dc_map = list(csv2dict)
    
    #print(dc_map)

    dc_map = sorted(dc_map, key = lambda d: float(d['distance']))

    # using enumerate() + next() to find index of
    # first element just greater than 0.6
    res = next(x for x, val in enumerate(dc_map)
               if float(val['distance']) >= dist)

    return dc_map[res]['cooldown']

def update_last_loc(lat,lng):
    with open("last_loc.csv", mode="w", newline='') as csvfile:
        fieldnames = ['lat','lng']
        locwriter = csv.DictWriter(csvfile,fieldnames)
        locwriter.writeheader()
        locwriter.writerow({'lat':lat,'lng':lng})

def set_location(devices, lat, lng):
    update_last_loc(lat,lng)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
        e.map(set_loc, devices, repeat(lat), repeat(lng))


def set_loc(device, lat, lng):
    device_lockdown_client = LockdownClient(device.serial)
    location_simulator = DtSimulateLocation(lockdown=device_lockdown_client)
    location_simulator.set(lat, lng)

def walk(latitude, longitude, seconds_to_walk, meters_per_step_base):
    the_devices = list_devices()

    dist = round(dist_from_last(latitude,longitude),2)

    print(f"distance from last = {dist}")

    cool = cooldown(dist)
    print(f"cooldown =  {cool}")

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

    # Walk 'meters_per_step' ( +/- a little delta ) in the 'step_direction' until target_dur is exceeded. First head one
    # way out for 'seconds_to_walk' seconds, and then head the opposite direction back
    while elapsed < target_dur:
        current = time.time()
        elapsed = current - start
        step_direction = math.radians(random.uniform(0, 360))  # because why not
        start_point = next_point
        for direction in (step_direction, step_direction - math.pi, step_direction - math.pi, step_direction):
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Simulate walking for all connected devices')
    parser.add_argument('-s', '--secs', metavar='N', default=100, type=int,
                    help='approx number of seconds to walk out before turning around')
    parser.add_argument('-m','--mps', metavar='M', default=3, type=float,
                    help='approx meters per second to walk')
    parser.add_argument('nums', metavar='lat,lng (no spaces)', type=str,
                    help='two comma-separated numbers representing latitude and longitude')
    args = parser.parse_args()

    latlng = get_latlng(args.nums)

    num1_str, num2_str = latlng.split(",")
    latitude = float(num1_str.strip())
    longitude = float(num2_str.strip())
    seconds_to_walk = args.secs
    meters_per_step_base = args.mps

    print(f"lat = {latitude}, lng = {longitude}")
    print(f"secs = {seconds_to_walk}")
    print(f"meters per second = {meters_per_step_base}")
    walk(latitude, longitude, seconds_to_walk, meters_per_step_base)

if __name__ == "__main__":
  main()