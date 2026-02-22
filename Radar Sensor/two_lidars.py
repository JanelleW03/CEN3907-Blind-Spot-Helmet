from gpiozero import RGBLED, PWMOutputDevice, Button, DistanceSensor
from time import sleep
import serial, time
import numpy as np

# UD = DistanceSensor(echo=17, trigger=4, max_distance=4)
motor1 = PWMOutputDevice(26)
motor2 = PWMOutputDevice(27) # change this
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
ser2 = serial.Serial("/dev/serial1", 115200, timeout=0)

def read_tfluna_data1():
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

def read_tfluna_data2():
    start = time.time()
    while time.time() - start < 0.02:
    	counter = ser2.in_waiting
        if counter > 8:
        	bytes_serial = ser2.read(9)
            ser2.reset_input_buffer()

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

if ser2.isOpen() == False:
        ser2.open()

def toggle_system():
        global button_state
        button_state = not button_state
        print("System ON" if button_state else "System OFF")

# button management
button.when_released = toggle_system

while True:
	#distanceUD = UD.distance * 4

    distanceTF1, strength1, temp1 = read_tfluna_data1()
    distanceTF2, strength2, temp2 = read_tfluna_data2()
    vibration1 = calculate_vibration(distanceTF1)
    vibration2 = calculate_vibration(distanceTF2)

    if distanceTF1 is None:
        print(f"TFLuna1 timeout")
        continue

    if distanceTF2 is None:
        print(f"TFLuna2 timeout")
        continue

    if button_state: # button is pressed to turn on the system
        #print("System running")
        #print(f"Ultrasonic: {distanceUD:.3f} m | TF-Luna: {distanceTF:.3f} m")
        #print("vibration: ", vibration)
        print("distance1: ",  distanceTF1, "distance2: ", distanceTF2)
        if distanceTF1 < 0.5 and distanceTF2 > 0.5: # distanceUD < 0.5 and (for distance sensor reliability)
            led.color = (0, 1, 0) # Green
            motor1.value = vibration1
        elif distanceTF2 < 0.5 and distanceTF1 > 0.5:
            led.color = (0, 1, 0)
            motor2.value = vibration2
        elif distanceTF1 < 0.5 and distanceTF2 < 0.5: # somehow something on both sides?
            led.color = (0, 1, 0)
            motor1.value = vibration1
            motor2.value = vibration2
	else:
		print("System Idle")
		led.color(1, 0, 0) # Red when off
		motor1.value = 0
        motor2.value = 0
