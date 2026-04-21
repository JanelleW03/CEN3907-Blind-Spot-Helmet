from gpiozero import RGBLED, PWMOutputDevice, Button, DistanceSensor
from time import sleep
import serial, time
import numpy as np

import cv2
from picamera2 import Picamera2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision

THREAD_NUM = 4
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
DEFAULT_MODEL = 'efficientdet_lite0.tflite'
CORAL_MODEL = 'efficientdet_lite0_edgetpu.tflite'
FPS_POS = (20, 60)
FPS_FONT = cv2.FONT_HERSHEY_SIMPLEX
FPS_HEIGHT = 1.5
FPS_WEIGHT = 3
FPS_COLOR = (255, 0, 0)
FPS_AVG_FRAME_COUNT = 10
TRIGGER_CLASSES = {"car", "motorcycle", "bus", "truck", "person"}

# UD = DistanceSensor(echo=17, trigger=4, max_distance=4)
motor1 = PWMOutputDevice(27)
motor2 = PWMOutputDevice(26) 
led = RGBLED(22, 23, 24, active_high=False)
button = Button(17)
button_state = False
counter = 0

sleep(2)

def calculate_vibration(distance):
        vibration = (((distance - 0.02) * -1) / (4 - 0.02)) + 1
        return max(0.0, min(1.0, vibration))

def calculate_distance(duration):
        speed = 343
        distance = (speed * duration / 2)
        return distance

ser = serial.Serial("/dev/serial0", 115200, timeout=0)
ser2 = serial.Serial("/dev/ttyAMA1", 115200, timeout=0)

# Get image from the camera module
picam2 = Picamera2()
picam2.preview_configuration.main.size = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
picam2.preview_configuration.main.format = 'RGB888'
picam2.preview_configuration.main.align()
picam2.configure("preview")
picam2.start()

model = DEFAULT_MODEL

# Initialize the object detection model
base_options = core.BaseOptions(
        file_name=model, use_coral=False, num_threads=THREAD_NUM)
detection_options = processor.DetectionOptions(
        max_results=4, score_threshold=0.3)
options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
detector = vision.ObjectDetector.create_from_options(options)

def read_tfluna_data1():
    start = time.time()
    while time.time() - start < 0.1:
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
    while time.time() - start < 0.1:
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
#button.when_released = toggle_system
led.color = (0, 0, 1)
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

    if True: # button is pressed to turn on the system
        #print("System running")
        #print(f"Ultrasonic: {distanceUD:.3f} m | TF-Luna: {distanceTF:.3f} m")
        #print("vibration: ", vibration)
        print("distance1: ",  distanceTF1, "distance2: ", distanceTF2)
        #label = "cat"
        #led.color = (0, 0, 1)
        if distanceTF1 < 9.0 and distanceTF1 > 2.0: # distanceUD < 0.5 and (for distance sensor reliability)
             # Camera checking code here
             image = picam2.capture_array()
             counter += 1
             image = cv2.flip(image, -1)
             # Convert the image from BGR to RGB as required by the TFLite model
             image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

             # Create a TensorImage object from  the RGB image
             image_tensor = vision.TensorImage.create_from_array(image_RGB)

             # Run object detection estimation using the model
             detections = detector.detect(image_tensor)

             if detections.detections:
                  for det in detections.detections:
                        category = det.categories[0]
                        label = category.category_name
                        score = category.score
                
                        print(f"Detected: {label} ({score:.2f}) ")
                        if label in TRIGGER_CLASSES:
                             motor1.value = vibration1
                             led.color = (0, 1, 0) # Green
                             print("lidar1 detection")
                             break
                        else:
                             motor1.value = 0
                             led.color = (0, 0, 1)
                  continue

        else:
            led.color = (0, 0, 1)
            motor1.value = 0

        if distanceTF2 < 9.0 and distanceTF2 > 2.0:
              # Camera checking code here
             image = picam2.capture_array()
             counter += 1
             image = cv2.flip(image, -1)
             # Convert the image from BGR to RGB as required by the TFLite model
             image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

             # Create a TensorImage object from  the RGB image
             image_tensor = vision.TensorImage.create_from_array(image_RGB)

             # Run object detection estimation using the model
             detections = detector.detect(image_tensor)

             if detections.detections:
                  for det in detections.detections:
                        category = det.categories[0]
                        label = category.category_name
                        score = category.score
                
                        print(f"Detected: {label} ({score:.2f}) ")
                        if label in TRIGGER_CLASSES:
                             motor2.value = vibration1
                             led.color = (0, 1, 0) # Green
                             print("lidar2 detection")
                             break
                        else:
                             motor2.value = 0
                             led.color = (0, 0, 1)
                  continue
        else:
            motor2.value = 0
            led.color = (0, 0, 1)
            
    else:
        print("System Idle")
        led.color = (1, 0, 0) # Red when off
        motor1.value = 0
        motor2.value = 0
