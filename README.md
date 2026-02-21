# CEN3907-Blind-Spot-Helmet
Urban cyclists face safety risks from traffic and limited visibility. Traditional helmets protect the head but don’t enhance awareness. The Blind Spot Helmet uses radar-based detection and haptic feedback to alert riders of nearby vehicles in real time, improving safety for daily commuters on busy streets.

At a high level, our current architecture for this project is as follows. We utilize a Raspberry Pi 4 to poll two LiDAR sensors and interpret if there are any objects present within a predetermined range that could pose a risk to the user. If the LiDARs identify a potentially dangerous object, a haptic feedback sensor will be activated on the side that the object was detected to alert the user of its presence.

# Completed Work
We developed fully functioning code for the Pi 4 that polls the LiDAR sensors and successfully triggers haptic feedback on the side where an object was detected. 

In parallel, we are working on an implementation for the Raspberry Pi Pico, which is much more portable and consumes less power. At this point, we are currently testing LiDAR integration with Pico-specific code.

As for physical components within the project, we have gone through many iterations of 3d modules to house our system. The current one is robust and houses the Raspberry Pi as well as the sensors connected to it, with cutouts for charging and wiring.

# Known Bugs
The only main bug we have for our design at the moment is due to the physical connections between Raspberry Pi and sensors. Because we haven't soldered connections, as we are still testing multiple systems, our wiring is liable to disconnections during movement testing. This will be fixed once we have finalized our design and implement permanent connections.

# Onshape Design of Helmet Module
https://cad.onshape.com/documents/718453d0fac994bf19ba09c7/w/0e19fb7305c1e5489b3984cd/e/3690a92add8a8350898fd115?renderMode=0&uiState=69992bad388945be4745d517 
