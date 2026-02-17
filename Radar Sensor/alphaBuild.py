from gpiozero import RGBLED, PWMOutputDevice, Button, DistanceSensor
from time import sleep
import serial, time
import numpy as np

# UD = DistanceSensor(echo=17, trigger=4, max_distance=4)
motor = PWMOutputDevice(26)
led = RGBLED(10, 9, 11, active_high=True)
button = Button(17)
button_state = False

sleep(2)

def calculate_vibration(distance):
        vibration = (((distance - 0.02) * -1) / (4 - 0.02)) + 1
        return max(0.0, min(1.0, vibration))

def calculate_distance(duration):
        speed = 343
        distance = (speed * duration / 2)
        return distance

ser = serial.Serial("/dev/serial0", 115200, timeout=0)

def read_tfluna_data():
    start = time.time()
	while time.time() - start < 0.02:
    	counter = ser.in_waiting
        if counter > 8:
        	bytes_serial = ser.read(9)
            ser.reset_input_buffer()

            if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
                distance = bytes_serial[2] + bytes_serial[3]*256
                strength = bytes_serial[4] + bytes_serial[5]*256
                temperature = bytes_serial[6] + bytes_serial[7]*256
                temperature = (temperature/8.0) - 256.0
                ##print(distance)
                return distance/100.0, strength, temperature
    return None

if ser.isOpen() == False:
        ser.open()

def toggle_system():
        global button_state
        button_state = not button_state
        print("System ON" if button_state else "System OFF")

# button management
button.when_released = toggle_system

while True:
	#distanceUD = UD.distance * 4

    distanceTF, strength, temp = read_tfluna_data()
    vibration = calculate_vibration(distanceTF)

    if distanceTF is None:
        print(f"TFLuna timeout")
        continue

    if button_state: # button is pressed to turn on the system
        #print("System running")
        #print(f"Ultrasonic: {distanceUD:.3f} m | TF-Luna: {distanceTF:.3f} m")
        #print("vibration: ", vibration)
        print("distance: ",  distanceTF)
        if distanceTF < 0.5: # distanceUD < 0.5 and (for distance sensor reliability)
            led.color = (0, 1, 0) # Green
            motor.value = vibration
	else:
		print("System Idle")
		led.color(1, 0, 0) # Red when off
		motor.value = 0
