#include <AltSoftSerial.h>
#include "DFRobot_mmWave_Radar.h"

// This code demonstrates a faster radar sensor detection with the use of AltSoftSerial instead of the SoftwareSerial that was used in the original example code
// also the built-in LED should be blinking as long as the sensor received power 
// The TX and DX have to be RX=D8 and TX=D9 becuase of this serial
// Also another important thing to mention the baud has to 115200

// Important things to note:
// the radar can only sense movement around it (aka if the sensor is moving but there is nothing around it won't detect anything)
// the arduino seems to consistrently disconnect, have tried switching cables and switching arduinos with little luck

AltSoftSerial mySerial;              // RX=D8, TX=D9
DFRobot_mmWave_Radar sensor(&mySerial);

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(115200);        
  mySerial.begin(115200);

  //sensor.factoryReset();
  //sensor.DetRangeCfg(0, 1);
  //sensor.OutputLatency(0, 0);
}

void loop() {
  int val = sensor.readPresenceDetection();
  digitalWrite(LED_BUILTIN, val ? HIGH : LOW);
  Serial.print("value ");
  Serial.println(val);
  delay(50);
}
