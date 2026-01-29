from time import time, sleep
from gpiozero import InputDevice, OutputDevice, PWMOutputDevice
import sys
import serial

import cv2
from picamera2 import Picamera2
from tflite_support.task import core
from tflite_support.task import processor
from tflite_support.task import vision
import utils


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
HAPTIC_PIN = 14
TRIGGER_CLASSES = {"person", "cat", "dog"}


def main():
    # Coral USB Accelerator will not be used in this project
    # modify here if it'll be used
    detect(True, DISPLAY_WIDTH, DISPLAY_HEIGHT, THREAD_NUM, False)

def detect(csi_camera: bool, width: int, height: int, num_threads: int, enable_edgetpu: bool):
    """
        Continuously run inference on images acquired from the camera.

        Args:
        csi_camera: True/False whether the Raspberry Pi camera module is a CSI Camera (Pi Camera module).
        width: the width of the frame captured from the camera.
        height: the height of the frame captured from the camera.
        num_threads: the number of CPU threads to run the model.
        enable_edgetpu: True/False whether the model is a EdgeTPU model.
    """

    # GPIO Setup
    ser = serial.Serial("/dev/serial0", 115200, timeout=0)
    motor = PWMOutputDevice(HAPTIC_PIN)
    motor.value = 0

    counter, fps = 0, 0
    fps_start_time = time.time()

    # Get image from the camera module
    if csi_camera:
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (width, height)
        picam2.preview_configuration.main.format = 'RGB888'
        picam2.preview_configuration.main.align()
        picam2.configure("preview")
        picam2.start()
    else:
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # enable Coral TPU if it's used
    if enable_edgetpu:
        model = CORAL_MODEL
    else:
        model = DEFAULT_MODEL

    # Initialize the object detection model
    base_options = core.BaseOptions(
        file_name=model, use_coral=enable_edgetpu, num_threads=num_threads)
    detection_options = processor.DetectionOptions(
        max_results=4, score_threshold=0.3)
    options = vision.ObjectDetectorOptions(
        base_options=base_options, detection_options=detection_options)
    detector = vision.ObjectDetector.create_from_options(options)

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
			
            if distance < 5: # Hardcoded value, figure out what distance means
                image = picam2.capture_array()

                counter += 1
                image = cv2.flip(image, -1)

                # Convert the image from BGR to RGB as required by the TFLite model
                image_RGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Create a TensorImage object from  the RGB image
                image_tensor = vision.TensorImage.create_from_array(image_RGB)

                # Run object detection estimation using the model
                detections = detector.detect(image_tensor)

	            # Replacement code!!!!
                if detections.detections:
    	            for det in detections.detections:
                        category = det.categories[0]
                        label = category.category_name
                        score = category.score
                
                        bbox = det.bounding_box
                        print(f"Detected: {label} ({score:.2f}) "
                                f"at x={bbox.origin_x}, y={bbox.origin_y}, "
                                f"w={bbox.width}, h={bbox.height}")
                        if label in TRIGGER_CLASSES:
                            motor.value = 5 # hardcoded vibration amount
                            sleep(0.1)
                            motor.value = 0

if __name__ == '__main__':
    main()