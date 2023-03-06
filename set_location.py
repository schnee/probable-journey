import argparse
import time

from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.simulate_location import DtSimulateLocation
from pymobiledevice3.usbmux import list_devices

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


def set_location(devices, lat, lng):
    for device in devices:
        # print(device)
        device_lockdown_client = LockdownClient(device.serial)

        # image_mounter = MobileImageMounterService(lockdown=device_lockdown_client)
        # image = '/home/brent/projects/Xcode_Developer_Disk_Images/Developer Disk Image/15.7/DeveloperDiskImage.dmg'
        # signature = image + '.signature'
        #
        # image = Path(image).read_bytes()
        # signature = Path(signature).read_bytes()

        # image_mounter.upload_image('Developer', image, signature)
        # image_mounter.mount('Developer', signature)

        location_simulator = DtSimulateLocation(lockdown=device_lockdown_client)
        location_simulator.set(lat, lng)


while 1 == 1:
    set_location(the_devices, latitude, longitude)
    time.sleep(5)
    set_location(the_devices, latitude + 0.0001, longitude + 0.0001)
    time.sleep(5)
    set_location(the_devices, latitude + 0.0002, longitude + 0.0002)
    time.sleep(5)
    set_location(the_devices, latitude + 0.0003, longitude + 0.0003)
    time.sleep(5)
    set_location(the_devices, latitude + 0.0002, longitude + 0.0002)
    time.sleep(5)
    set_location(the_devices, latitude + 0.0001, longitude + 0.0001)
    time.sleep(5)
    set_location(the_devices, latitude, longitude)
    time.sleep(5)
