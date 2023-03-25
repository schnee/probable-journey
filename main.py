# This is a sample Python script.
import math
import random
import time
import concurrent.futures


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name, other):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}, {other}')  # Press Ctrl+F8 to toggle the breakpoint.
    start = time.time()
    time.sleep(.1)
    elapsed = time.time() - start
    print(f'Elapse: {elapsed}')
    meters_per_step_base = 3
    step_range = meters_per_step_base * 0.1
    print(random.uniform(meters_per_step_base - step_range, meters_per_step_base + step_range))
    uniform = random.uniform(0, 360)
    print(uniform, math.radians(uniform))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm', 2)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as e:
        e.submit(print_hi, 'thread1', 3)
        e.submit(print_hi, 't2', 4)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
