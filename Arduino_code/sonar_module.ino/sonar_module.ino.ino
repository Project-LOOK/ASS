// millis() rolls over @ 512k


// Import libraries (BLEPeripheral depends on SPI)
#include <SPI.h>
#include <BLEPeripheral.h>
#include <NewPing.h>

// LED and button pin
#define LED_PIN     7
#define BUTTON_PIN  6
#define TRIG_PIN  12
#define ECHO_PIN  11

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
boolean LED_STATUS = true;
#define MAX_DISTANCE 400

NewPing sonar(TRIG_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200);

  // set LED pin to output mode, button pin to input mode
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

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

  Serial.println("BLE Sonar Module");
}

void loop() {
  blePeripheral.poll();
  new_millis = millis();

  if ((new_millis - old_millis) > 100) {
    updateTime();
    updateDistance();
    old_millis = new_millis;
    if(lastPrint != seconds) {
      printTime();
      printDistance();
      lastPrint = seconds;
    }
  }
}

void updateDistance() {
  dst = sonar.ping_cm();
  ble_char_dst.setValue(dst);
}

void printDistance() {
  Serial.println(dst, DEC);
}

void toggleLED() {
  digitalWrite(LED_PIN, LED_STATUS);
  LED_STATUS = !LED_STATUS;
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


