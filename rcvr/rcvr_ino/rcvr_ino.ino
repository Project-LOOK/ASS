#include <LiquidCrystal.h>
#include <SoftwareSerial.h>
#include <NewPing.h>

// MAKE SURE THESE PINS MATCH CURRENT SETUP
// LCD pins
const int rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
// BT pins
const int rx = 8, tx = 9;

const int WAIT_MS = 200;
const int MAX_DIST = 500;

unsigned int dist_cm;
unsigned long m1 = 0;
unsigned long m2 = 0;

char buff;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
SoftwareSerial mySerial(rx, tx);
NewPing sonar(trigPin, echoPin, MAX_DIST);


void setup() {
  lcd.begin(20, 4);
  lcd.setCursor(0,3);
  lcd.print("Distance:");

  Serial.begin(9600);
  while(!Serial){
  }
  mySerial.begin(9600);
}

void loop() {

  // Print command and send to BT mod
  if(Serial.available()) {
    lcd.setCursor(0,0);
    lcd.print("                    ");
    lcd.setCursor(0,0);
    while(Serial.available()) {
      buff = Serial.read();
      lcd.write(buff);
      Serial.write(buff);
      mySerial.write(buff);   
    }
    Serial.write(": ");
  } 

  // Read BT result & print to LCD/Serial
  if(mySerial.available()) {
    lcd.setCursor(10,3);
    while(mySerial.available()) {
      buff = mySerial.read();
      Serial.write(buff);
      lcd.write(buff);
    }
    Serial.write('\n');
  }
}









