#include <NewPing.h>
#include <SoftwareSerial.h>

// Sonar pins 
const int trigPin = 12, echoPin = 11;
// Bluetooth pins
const int rx = 8, tx = 9;

const int wait_mds = 500;
char b;
char buff[4];

long dist_cm;
#define MAX_DISTANCE 400
NewPing sonar(trigPin, echoPin, MAX_DISTANCE);

SoftwareSerial mySerial(rx, tx);

void setup() {
  Serial.begin(9600);
  while(!Serial) {
  }

  mySerial.begin(9600);
  delay(500);
  
}

void loop() {
  
  dist_cm = sonar.ping_cm();
  snprintf(buff, 4, "%3d", dist_cm);
  Serial.println(buff);
  mySerial.print(buff);
  delay(200);
  

}

