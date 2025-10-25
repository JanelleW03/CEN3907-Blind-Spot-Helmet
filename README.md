# CEN3907-Blind-Spot-Helmet
Urban cyclists face safety risks from traffic and limited visibility. Traditional helmets protect the head but don’t enhance awareness. The Blind Spot Helmet uses radar-based detection and haptic feedback to alert riders of nearby vehicles in real time, improving safety for daily commuters on busy streets.

At a high level, our current architecture for this project is as follows. We will use a microprocessor, such as the Raspberry Pi 4, to communicate with the different components, though currently for prototyping, we are using the more simpler Arduino. We will have a radar sensor on our helmet which will send its data to the microprocessor, when it detects motion. This will then prompt the microprocessor to read in the image data from an attached camera sensor and we will use a pretrained model stored on the microprocessor to identify if the object is a dangerous vehicle, or a less dangerous person, animal, etc. If a dangerous object is detected in the blind spot, our haptic sensors will emit a light buzz to notify the biker. 

# Completed Work
Created a simulation of radar and haptic sensor communication in TinkerCad with an Arduino. We used a vibration sensor, an ultrasonic distance sensor, and an Arduino Uno R3 for this simulation to check the communication between the sensors. It currently causes the sensor to vibrate if the distance sensor detects anything within a 50 cm range. 

Created a very simple convolutional neural network to mimic what our final model might look like. This references a Kaggle dataset with images of different vehicle types and pedestrians. This simple CNN seeks to classify images, and the weights from our final model can be stored on the microprocessor. 

As a team, we have also done extensive research on the different possible components we will use for this project, documented in our pre alpha build report. We have also included sketches of how our hardware will be integrated with the physical helmet, and plans for how we will use a Raspberry Pi to communicate with all the components. We also gave consideration to how we will plan for sensor failure, and the physical resilience of this helmet.

# Known Bugs
We are currently using a vibration sensor instead of a traditional piezo haptic sensor, because there is some difficult in getting the piezo to vibrate. 

The CNN has low accuracy right now, not much higher than baseline guessing. This is because the model has not been optimized yet for the dataset, so as it is right now, the model needs improvement, but is a good baseline for what potential CNN architecture to use. It may end up needing to be replaced by pretrained weights from transfer learning.
