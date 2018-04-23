// millis() rolls over @ 512k

// Import libraries (BLEPeripheral depends on SPI)
#include <SPI.h>
#include <BLEPeripheral.h>
#include <NewPing.h>
#include <Adafruit_NeoPixel.h>

// LED definitions
#define LED_PIN   13
#define NUM_LEDS   8

// Sonar definitions
#define TRIG_PIN  12
#define ECHO_PIN  11
#define INTERVAL  50
#define MAX_DISTANCE 400



BLEPeripheral blePeripheral = BLEPeripheral();
BLEService sonar_svc = BLEService("19b10010e8f2537e4f6cd104768a1214");
// Characteristics, (must start with svc + 1)
BLEUnsignedIntCharacteristic ble_char_dst = BLEUnsignedIntCharacteristic("19b10011e8f2537e4f6cd104768a1214", BLERead | BLENotify);

// Setup for Distance Sensor
unsigned int dst = 10;

unsigned long old_millis;
unsigned long new_millis;
unsigned long seconds = 0;
unsigned long minutes = 0;
unsigned long hours = 0;
unsigned long overflows = 0;
unsigned long lastPrint = 0;
unsigned long pseconds = 0;
unsigned int index2 = 0;
long int b = 0;
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, LED_PIN, NEO_GRBW + NEO_KHZ800);
uint32_t Wheel(byte WheelPos);

unsigned long brightness = 50;
byte neopix_gamma[] = {
  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
  1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
  2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
  5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
  10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
  17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
  25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
  37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
  51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
  69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
  90, 92, 93, 95, 96, 98, 99, 101, 102, 104, 105, 107, 109, 110, 112, 114,
  115, 117, 119, 120, 122, 124, 126, 127, 129, 131, 133, 135, 137, 138, 140, 142,
  144, 146, 148, 150, 152, 154, 156, 158, 160, 162, 164, 167, 169, 171, 173, 175,
  177, 180, 182, 184, 186, 189, 191, 193, 196, 198, 200, 203, 205, 208, 210, 213,
  215, 218, 220, 223, 225, 228, 231, 233, 236, 239, 241, 244, 247, 249, 252, 255
};

unsigned int avg[] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
unsigned int index1 = 0;

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200);

  // set advertised local name and service UUID
  blePeripheral.setLocalName("Sonar Module 1");
  blePeripheral.setDeviceName("Sonar Module 1");
  blePeripheral.setAdvertisedServiceUuid(sonar_svc.uuid());

  // add service and characteristics
  blePeripheral.addAttribute(sonar_svc);
  blePeripheral.addAttribute(ble_char_dst);

  ble_char_dst.setValue(0);

  blePeripheral.setEventHandler(BLEConnected, blePeripheralConnectHandler);
  blePeripheral.setEventHandler(BLEDisconnected, blePeripheralDisconnectHandler);

  blePeripheral.begin();

  strip.begin();
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(255, 255, 255, 255));
    strip.show();
  }
  
  //strip.setBrightness(brightness);  
  strip.show(); // Initialize all pixels to 'off'

  Serial.println("BLE Sonar Module");
}

void loop() {
  blePeripheral.poll();
  //new_millis = millis();

  //if ((new_millis - old_millis) > 50) {
    //updateTime();
    updateDistance();
    updateBrightness();
    //old_millis = new_millis;
    delay(INTERVAL);
    /*if(lastPrint != seconds) {
      printTime();
      printDistance();
      lastPrint = seconds;
    }*/
   //}
}

void updateBrightness() {
    index2 = index1 % 11;
    avg[index2] = dst;
    Serial.print("Index: ");
    Serial.println(index2);
    index1++;

    brightness = 0;
    for (int ii = 0; ii < 11; ii++) {
      brightness += (long)avg[ii]; 
    }
    brightness = (dst + brightness) / 12;

    b = 255 - 5*(brightness);
    if (b < 0) {
      b = 0;
    }
    Serial.println(b);
  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, strip.Color(b, b, b, b));
  }
  strip.show();
}

void updateDistance() {
  dst = sonar.ping_cm();
  ble_char_dst.setValue(dst);
}

void printDistance() {
  Serial.println(dst, DEC);
}

void blePeripheralConnectHandler(BLECentral & central) {
  Serial.print(F("Connected event, central: "));
  Serial.println(central.address());
}

void blePeripheralDisconnectHandler(BLECentral & central) {
  Serial.print(F("Disconnected event, central: "));
  Serial.println(central.address());
}

void updateTime() {
  if (old_millis > new_millis)
    overflows += 512;
  seconds = overflows + new_millis / 1000;
}

void printTime() {
  hours = seconds / 3600;
  minutes = (seconds - hours * 3600) / 60;
  pseconds = (seconds - hours * 3600 - minutes * 60);

  Serial.print(hours);
  Serial.print(":");
  Serial.print(minutes);
  Serial.print(":");
  Serial.println(pseconds);
}

// Input a value 0 to 255 to get a color value.
// The colours are a transition r - g - b - back to r.
uint32_t Wheel(byte WheelPos) {
  WheelPos = 255 - WheelPos;
  if (WheelPos < 85) {
    return strip.Color(255 - WheelPos * 3, 0, WheelPos * 3, 0);
  }
  if (WheelPos < 170) {
    WheelPos -= 85;
    return strip.Color(0, WheelPos * 3, 255 - WheelPos * 3, 0);
  }
  WheelPos -= 170;
  return strip.Color(WheelPos * 3, 255 - WheelPos * 3, 0, 0);
}
