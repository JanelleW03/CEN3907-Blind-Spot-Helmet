import serial, time
import numpy as np

ser = serial.Serial("/dev/serial0", 115200, timeout=0)

def read_tfluna_data():
	while True:
		counter = ser.in_waiting
		if counter > 8:
			bytes_serial = ser.read(9)
			ser.reset_input_buffer()

			if bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59:
				distance = bytes_serial[2] + bytes_serial[3]*256
				strength = bytes_serial[4] + bytes_serial[5]*256
				temperature = bytes_serial[6] + bytes_serial[7]*256
				temperature = (temperature/8.0) - 256.0
				return distance/100.0, strength, temperature

if ser.isOpen() == False:
	ser.open()

distance, strength, temperature = read_tfluna_data()

print('Distance: {0:2.2f} m, Strength: {1:2.0f} / 65535 (16-bit), Chip Temperature: {2:2.1f} C'.\
		format(distance,strength,temperature))

ser.close()
