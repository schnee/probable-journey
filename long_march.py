import argparse
import time

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.simulate_location import DtSimulateLocation
from pymobiledevice3.usbmux import list_devices
from datetime import timedelta
from haversine import inverse_haversine, Direction, Unit

# Parse command line arguments
parser = argparse.ArgumentParser(description='Accept two comma-separated numbers')
parser.add_argument('nums', metavar='num1,num2', type=str,
                    help='two comma-separated numbers')
args = parser.parse_args()

num1_str, num2_str = args.nums.split(",")
latitude = float(num1_str)
longitude = float(num2_str)

print(f"num1 = {latitude}, num2 = {longitude}")

the_devices = list_devices()


# image_mounter = MobileImageMounterService(lockdown=device_lockdown_client)
# image = '/home/brent/projects/Xcode_Developer_Disk_Images/Developer Disk Image/15.7/DeveloperDiskImage.dmg'
# signature = image + '.signature'
#
# image = Path(image).read_bytes()
# signature = Path(signature).read_bytes()

# image_mounter.upload_image('Developer', image, signature)
# image_mounter.mount('Developer', signature)

# the sleep time is set to 1 second, so that we're moving meters_per_step / second. This might
# get randomized a bit in the future
def set_location(devices, lat, lng):
    for device in devices:
        # print(device)
        device_lockdown_client = LockdownClient(device.serial)
        location_simulator = DtSimulateLocation(lockdown=device_lockdown_client)
        location_simulator.set(lat, lng)
    time.sleep(1)


start = time.time()
now = start
target_dur: float = 2 * 60 * 60  # two hours * 60 minutes * 60 seconds
elapsed = 0

meters_per_step = 3
step_direction = Direction.SOUTHEAST # because why not

# Walk 'meters_per_step' in the 'step_direction' until target_dur is exceeded. First head one way out
# and then head the opposite direction back
while elapsed < target_dur:
    current = time.time()
    elapsed = current - start
    print(timedelta(seconds=round(elapsed)))
    for i in range(1000):
        next_point = inverse_haversine((latitude,longitude), meters_per_step * i, step_direction, Unit.METERS)
        set_location(the_devices, next_point[0], next_point[1])
    for i in range(999, 0, -1):
        next_point = inverse_haversine((latitude, longitude), meters_per_step * i, step_direction, Unit.METERS)
        set_location(the_devices, next_point[0], next_point[1])
