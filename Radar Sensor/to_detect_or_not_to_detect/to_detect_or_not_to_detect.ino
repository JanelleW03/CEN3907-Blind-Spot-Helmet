#include <SoftwareSerial.h>
#include "DFRobot_mmWave_Radar.h"
SoftwareSerial mySerial(3, 2);
DFRobot_mmWave_Radar sensor(&mySerial);
int ledPin = 13;
void setup()
{
Serial.begin(115200);
mySerial.begin(115200);
pinMode(ledPin, OUTPUT);
sensor.factoryReset(); //Restore to the factory settings
sensor.DetRangeCfg(0, 1); //The detection range is as far as 9m
sensor.OutputLatency(0, 0);
}

void loop()
{
int val = sensor.readPresenceDetection();
digitalWrite(ledPin, val);
Serial.print("value ");
Serial.println(val);
}