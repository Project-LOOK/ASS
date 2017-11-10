#include <LiquidCrystal.h>
#include <SoftwareSerial.h>
#include <NewPing.h>

// MAKE SURE THESE PINS MATCH CURRENT SETUP
// LCD pins
const int rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
// BT pins
const int rx = 8, tx = 9;
// Sonar pins
const int trigPin = 12, echoPin = 11;

const int WAIT_MS = 500;
const int MAX_DIST = 500;

const char RCVR_MAC[] ="341513879871";

unsigned int dist_cm;
unsigned long m1 = 0;
unsigned long m2 = 0;

char buff;
char print_str[6];

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

  connect();


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
    lcd.setCursor(0,1);
    lcd.print("                    ");
    lcd.setCursor(0,1);
    while(mySerial.available()) {
      buff = mySerial.read();
      Serial.write(buff);
      lcd.write(buff);
    }
    Serial.write('\n');
  }

  // Read sensor & print to LCD every X ms
  m2 = millis();
  if(m2 - m1 >= WAIT_MS) {
    m1 = m2;
    dist_cm = sonar.ping_cm();
    //Serial.write(dist_cm);
    snprintf(print_str,6,"%3ucm",dist_cm);
    lcd.setCursor(10,3);
    lcd.print(print_str);
   mySerial.print(print_str); 
  }
}

void connect() {
  int not_connected = true;

  while(not_connected) {
    Serial.print('Sending connection request');
  Serial.write("AT+CON341513879871");
  mySerial.write("AT+CON341513879871");

    delay(50);
    unsigned int con;
    while(mySerial.available()) {
      con = mySerial.read();
      Serial.print(con);
      Serial.print("\nwaiting...\n");
      if (con==65)
        not_connected = false;
    }
  }
}
