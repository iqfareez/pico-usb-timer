import board
import digitalio
import time
from adafruit_debouncer import Debouncer
import microcontroller

D = digitalio.DigitalInOut(board.GP5)
C = digitalio.DigitalInOut(board.GP4)
B = digitalio.DigitalInOut(board.GP3)
A = digitalio.DigitalInOut(board.GP2)

btn1 = digitalio.DigitalInOut(board.GP20)
start_btn = digitalio.DigitalInOut(board.GP18)

D.direction = digitalio.Direction.OUTPUT
C.direction = digitalio.Direction.OUTPUT
B.direction = digitalio.Direction.OUTPUT
A.direction = digitalio.Direction.OUTPUT

btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.UP
btn_val = Debouncer(btn1)

start_btn.direction = digitalio.Direction.INPUT
start_btn.pull = digitalio.Pull.UP
start_val = Debouncer(start_btn)

start_monotonic = 0  # will update when button Start is pressed

max_hour = 2**4  # 2 ^ bits
hour = 0

started = False
finished = False


def binary_clock(my_value):
    if my_value & 0b01:
        D.value = True
    else:
        D.value = False
    if my_value & 0b10:
        C.value = True
    else:
        C.value = False
    if my_value & 0b100:
        B.value = True
    else:
        B.value = False
    if my_value & 0b1000:
        A.value = True
    else:
        A.value = False


# return true when finished
def check_countdown():
    time_elapsed = time.monotonic() - start_monotonic
    hour_elapsed = int(time_elapsed /
                       60)  # for debugging, can convert to minute
    print(f'Hour elapsed: {hour_elapsed}')

    # for debugging
    print(f'Elapsed seconds {time_elapsed}s')

    # check remaining
    remaining_hour = hour - hour_elapsed
    print(f'Remaining hour: {remaining_hour}')
    binary_clock(remaining_hour)

    # return true when finished
    return remaining_hour == 0


while True:
    # Check for input
    btn_val.update()
    start_val.update()

    if btn_val.fell:
        hour += 1
        if hour >= max_hour:
            hour = 0
        print(hour)
        binary_clock(hour)

    if start_val.fell and not started:
        start_monotonic = time.monotonic()
        started = True
        print('Pressed')
        print(f'countdown from {hour}h has started')

    if started:
        time.sleep(.09)  # to reduce the checking freq
        res = check_countdown()

        # if finish, do the following
        if res:

            # TODO: make beep
            print('Resetting')
            time.sleep(2)
            microcontroller.reset()  # hard-reset the microcontroller
