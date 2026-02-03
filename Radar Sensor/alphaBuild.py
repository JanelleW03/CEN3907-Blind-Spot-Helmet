from gpiozero import InputDevice, OutputDevice, PWMOutputDevice, Button, DistanceSensor
from time import sleep
import serial, time
import numpy as np

UD = DistanceSensor(echo=17, trigger=4, max_distance=4)
motor = PWMOutputDevice(22)
led = OutputDevice(27)
button = Button(10)
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
	distanceUD = UD.distance * 4
	vibration = calculate_vibration(distanceUD)

	distanceTF, strength, temp = read_tfluna_data()

	if distanceTF is None:
		print(f"TFLuna timeout")
		continue

	if button_state: # button is pressed to turn on the system
		#print("System running")
		print(f"Ultrasonic: {distanceUD:.3f} m | TF-Luna: {distanceTF:.3f} m")
		#print("vibration: ", vibration)
		if distanceUD < 0.5 and distanceTF < 0.5:
			led.on()
			motor.value = vibration
		else:
			led.off()
			motor.value = 0
	else:
		print("System Idle")
		led.off()
		motor.value = 0

