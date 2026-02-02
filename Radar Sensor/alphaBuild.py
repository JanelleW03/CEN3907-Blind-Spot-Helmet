from gpiozero import InputDevice, OutputDevice, PWMOutputDevice, Button
from time import sleep
import serial, time
import numpy as np

trig = OutputDevice(4)
echo = InputDevice(17)
motor = PWMOutputDevice(22)
led = OutputDevice(27)
button = Button(10)
button_state = False

sleep(2)

def get_pulse_time():
        timeout = time.time() + 0.02 # 20ms
        while echo.is_active:
                if time.time() > timeout:
                        return None

        trig.on()
        sleep(0.00001)
        trig.off()

        timeout = time.time() + 0.02 # 20ms
        while echo.is_active == False:
                if time.time() > timeout:
                        return None
        pulse_start = time.time()

        timeout = time.time() + 0.02 # 20ms
        while echo.is_active == True:
                if time.time() > timeout:
                        return None
        pulse_end = time.time()

        sleep(0.06)

        return pulse_end - pulse_start

def calculate_vibration(distance):
        vibration = (((distance - 0.02) * -1) / (4 - 0.02)) + 1
        return vibration

def calculate_distance(duration):
        speed = 343
        distance = (speed * duration / 2)
        return distance

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
                                ##print(distance)
                                return distance/100.0, strength, temperature

if ser.isOpen() == False:
        ser.open()


def toggle_system():
    global button_state
    button_state = not button_state
    print("System ON" if button_state else "System OFF")


while True:
        duration = get_pulse_time()
        if duration is None:
                print("UD timeout")
                continue
		
        distanceUD = calculate_distance(duration)
        vibration = calculate_vibration(distanceUD)

        distanceTF, strength, temp = read_tfluna_data()

        #if distanceTF is not None:
                #print(f"TFLuna has some distance: {distanceTF:.3f} m")
        #else:
                #print("there is not TFLuna data")

        # button state management
        button.when_pressed = toggle_system

        if button_state: # button is pressed to turn on the system
                ##dis = distance * 100
                print(f"Ultrasonic: {distanceUD:.3f} m | TF-Luna: {distanceTF:.3f} m")
                ## print("vibration: ", vibration)
                if distanceUD < 0.05 and distanceTF < 0.05:
                        led.on()
                        motor.value = vibration
                else:
                        led.off()
                        motor.value = 0
        else:
                led.off()
                motor.value = 0  
        sleep(0.0001)
