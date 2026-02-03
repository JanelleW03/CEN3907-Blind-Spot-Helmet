# CEN3907-Blind-Spot-Helmet
Urban cyclists face safety risks from traffic and limited visibility. Traditional helmets protect the head but don’t enhance awareness. The Blind Spot Helmet uses radar-based detection and haptic feedback added by AI based camera detection to alert riders of nearby vehicles in real time, improving safety for daily commuters on busy streets.

At a high level, our current architecture for this project is as follows. We will use the Raspberry Pi 4, to communicate with the camera. For now we have an Arduino UNO handling the logic behind the radar sensor with a distance sensor as a fail-safe. As we continue the protyping process we will have a radar sensor on our helmet which will send its data to the microprocessor, when it detects motion. This will then prompt the microprocessor to read in the image data from an attached camera sensor and we will use a pretrained model stored on the microprocessor to identify if the object is a dangerous vehicle, or a less dangerous person, animal, etc. If a dangerous object is detected in the blind spot, our haptic sensors will emit a light buzz to notify the biker. 

# Completed Work
We developed a simulation to test communication between radar and haptic feedback sensors using an Arduino Uno R3. The setup includes a vibration motor and an ultrasonic distance sensor, and is programmed so that the haptic motor activates only when the radar detects motion and the ultrasonic sensor identifies an object within a 50 cm range.

In parallel, we built a simplified convolutional neural network to serve as an early prototype of our planned final model. Using a Kaggle dataset containing images of various vehicle types and pedestrians, this CNN performs basic image classification. The ultimate goal is to store the trained model weights on a microprocessor for real-time inference.

As a team, we’ve also conducted extensive research on potential hardware components, which we documented in our pre-alpha build report. This includes initial sketches of how the electronics will be integrated into the helmet and a system architecture showing how a Raspberry Pi will coordinate communication among all sensors. We also evaluated strategies for handling sensor failure and improving the physical durability of the helmet.

# Known Bugs
We are currently using a vibration sensor, piezo haptic sensor, and LED to demonstrate our proof of concept, as our priority right now is optimizing AI-assisted detection on the Raspberry Pi. Due to the Arduino’s limited processing capabilities, especially when working with the radar sensor, the detection is not as fast as needed. These issues will be resolved once all components are transfered to the Raspberry Pi, though we have also researched alternatives like the Arduino Nano in case a secondary microcontroller is needed.

The example model downloaded onto the Raspberry Pi is very slow as well, reading only about 5 frames per second. Ideally, this should be much faster when detecting objects on the helmet. 

# Onshape Design of Helmet Module
https://cad.onshape.com/documents/718453d0fac994bf19ba09c7/w/0e19fb7305c1e5489b3984cd/e/2fc86442675e4b3da09defcf?renderMode=0&uiState=697d17874ebd30078a4fd052
