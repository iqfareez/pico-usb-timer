import board
import digitalio
import time
from adafruit_debouncer import Debouncer
import microcontroller
import simpleio
import supervisor

D = digitalio.DigitalInOut(board.GP5)
C = digitalio.DigitalInOut(board.GP4)
B = digitalio.DigitalInOut(board.GP3)
A = digitalio.DigitalInOut(board.GP2)

btn1 = digitalio.DigitalInOut(board.GP11)
relay = digitalio.DigitalInOut(board.GP19)

D.direction = digitalio.Direction.OUTPUT
C.direction = digitalio.Direction.OUTPUT
B.direction = digitalio.Direction.OUTPUT
A.direction = digitalio.Direction.OUTPUT

relay.direction = digitalio.Direction.OUTPUT

btn1.direction = digitalio.Direction.INPUT
btn1.pull = digitalio.Pull.UP
btn_val = Debouncer(btn1)

start_monotonic = 0  # will update when button Start is pressed

max_hour = 2**4  # 2 ^ bits
hour = 0

started = False
finished = False

now = time.monotonic()  # Time in seconds since power on


def binary_clock(my_value):
    if my_value & 0b01:
        A.value = True
    else:
        A.value = False
    if my_value & 0b10:
        B.value = True
    else:
        B.value = False
    if my_value & 0b100:
        C.value = True
    else:
        C.value = False
    if my_value & 0b1000:
        D.value = True
    else:
        D.value = False


# return true when finished
def check_countdown():
    now = time.monotonic()
    time_elapsed = now - start_monotonic
    hour_elapsed = int(time_elapsed)  # for debugging, can convert to minute
    print(f"Hour elapsed: {hour_elapsed}")

    # for debugging
    print(f"Elapsed seconds {time_elapsed}s")

    # check remaining
    remaining_hour = hour - hour_elapsed
    print(f"Remaining hour: {remaining_hour}")
    binary_clock(remaining_hour)

    # return true when finished
    return remaining_hour == 0


while True:
    # Check for input
    btn_val.update()

    if btn_val.fell:
        hour += 1
        if hour >= max_hour:
            hour = 0
        print(hour)
        binary_clock(hour)
        started = False
        now = time.monotonic()

    if hour != 0 and (now + 5) < time.monotonic() and not started:
        print("Starting")
        simpleio.tone(board.GP18, 440, duration=0.1)
        start_monotonic = time.monotonic()
        started = True
        relay.value = True
        print(f"countdown from {hour}h has started")

    if started:
        time.sleep(0.09)  # to reduce the checking freq
        res = check_countdown()

        # if finish, do the following
        if res:
            relay.value = False
            simpleio.tone(board.GP18, 1911, duration=0.1)
            simpleio.tone(board.GP18, 233, duration=0.1)
            simpleio.tone(board.GP18, 1200, duration=0.1)
            print("Resetting")
            # time.sleep(2)
            # microcontroller.reset()  # hard-reset the microcontroller
            supervisor.reload()
