#include <LiquidCrystal.h>
#include <SoftwareSerial.h>

// Bluetooth pins
const int rx = 8, tx = 9;
// LCD pins
const int rs = 7, en = 6, d4 = 5, d5 = 4, d6 = 3, d7 = 2;

const int wait_ms = 100;
String buff = "";
char b;
long int dist_cm;
unsigned long old_millis;
unsigned long new_millis;
boolean connected = false;

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
SoftwareSerial btSerial(rx, tx);

void setup() {
  Serial.begin(9600);
  while(!Serial) {
  }
  btSerial.begin(9600);

  lcd.begin(0,0);
  lcd.clear();
  delay(500);
  lcd.print("Distance:");

  connect();
}

void loop() {
  delay(200);

  //uart_2_bt();
  //bt_2_uart();

  int jj = 0;
  while(jj < 3) {
    b = btSerial.read();
    //buff[jj] = btSerial.read();
    // bx = btSerial.read();
    //long x = btSerial.parseInt();
    Serial.print(b);
    jj++;
  } 
  Serial.println("");
  //lcd.setCursor(9,0);
  //lcd.print(buff);
}

void connect() {
  boolean asleep = true;
  b = 'x';
  while(asleep) {
    old_millis = millis();
    new_millis = millis();
    Serial.println(old_millis);
    Serial.println(new_millis);

    btSerial.print("AT");
    Serial.print("AT");
    while(new_millis - old_millis < 200) {
      new_millis = millis(); 

      while(btSerial.available()) {
        b = btSerial.read();
        Serial.print(b);
        if(b == 'K') {
          asleep = false;
          new_millis = new_millis + 200;
          break;
        }

      }
      Serial.println(new_millis);
    }
    Serial.println("ASLEEP)");
  }
  btSerial.write("AT+CON341513879871");

}

void uart_2_bt() {
  if(Serial.available()) {
    while(Serial.available()) {
      b = Serial.read();
      Serial.write(b);
      btSerial.write(b);   
    }
    Serial.write("\n");
  } 
}

void bt_2_uart() {
  if(btSerial.available()) {
    while(btSerial.available()) {
      b = btSerial.read();
      Serial.write(b);
    }
    Serial.write('\n');
  }
}






