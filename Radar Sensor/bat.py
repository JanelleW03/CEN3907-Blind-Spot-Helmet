from gpiozero import InputDevice, OutputDevice, PWMOutputDevice
from time import sleep, time

## to run code python 3 bat.py

trig = OutputDevice(4)
echo = InputDevice(17)
motor = PWMOutputDevice(14)
led = OutputDevice(18)

sleep(2)

def get_pulse_time():
    trig.on()
    sleep(0.00001)
    trig.off()

    while echo.is_active == False:
        pulse_start = time()

    while echo.is_active == True:
        pulse_end = time()

    sleep(0.06)

    return pulse_end - pulse_start

##print(get_pulse_time())

def calculate_vibration(distance):
    vibration = (((distance - 0.02) * -1) / (4 - 0.02)) + 1
    return vibration

def calculate_distance(duration):
    speed = 343
    distance = (speed * duration / 2)
    return distance

while True:
    duration = get_pulse_time()
    distance = calculate_distance(duration)
    vibration = calculate_vibration(distance)
    ##dis = distance * 100
    print(distance)
   ## print("vibration: ", vibration)
    if distance < 0.05:
        led.on()
        motor.value = vibration
        sleep(0.0001)
    else:
        led.off()
        motor.value = 0
        sleep(0.0001)
