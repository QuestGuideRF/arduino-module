#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Adafruit_BME280.h>
#include <MHZ19_uart.h>
#include "GyverButton.h"
#define SOIL_PIN A0
#define BUTTON_PIN 4
#define RELAY_PINS {12, 11, 10, 9}
#define SCREEN_SWITCH_TIME 5000
#define SENSOR_READ_TIME 2000
#define NUM_SCREENS 3
LiquidCrystal_I2C lcd(0x27, 20, 4);
Adafruit_BME280 bme;
MHZ19_uart mhz19;
GButton button(BUTTON_PIN, LOW_PULL, NORM_OPEN);
struct SensorData {
  int co2;
  float temp;
  float humidity;
  float pressure;
  int soilMoisture;
} sensors;
int currentScreen = 0;
unsigned long lastScreenTime = 0;
unsigned long lastSensorTime = 0;
int relayPins[] = RELAY_PINS;
void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 4; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], HIGH);
  }
  lcd.init();
  lcd.backlight();
  showStartupScreen();
  Wire.begin();
  if (!bme.begin(0x76)) {
    Serial.println("BME280 init failed!");
  }
  mhz19.begin(3, 2);
  mhz19.setAutoCalibration(false);
  button.setDebounce(50);
  delay(2000);
  readSensors();
  lastScreenTime = millis();
}
void loop() {
  unsigned long now = millis();
  if (now - lastSensorTime >= SENSOR_READ_TIME) {
    lastSensorTime = now;
    readSensors();
    sendSerialData();
  }
  button.tick();
  if (button.isClick()) {
    nextScreen();
  }
  if (now - lastScreenTime >= SCREEN_SWITCH_TIME) {
    nextScreen();
  }
}
void readSensors() {
  sensors.temp = bme.readTemperature();
  sensors.humidity = bme.readHumidity();
  sensors.pressure = bme.readPressure() / 100.0F;
  sensors.co2 = mhz19.getPPM();
  int rawSoil = analogRead(SOIL_PIN);
  sensors.soilMoisture = map(rawSoil, 1023, 0, 0, 100);
}
void nextScreen() {
  currentScreen = (currentScreen + 1) % NUM_SCREENS;
  lastScreenTime = millis();
  updateDisplay();
}
void updateDisplay() {
  lcd.clear();
  switch (currentScreen) {
    case 0: showEnvironmentScreen(); break;
    case 1: showSoilScreen(); break;
    case 2: showRelayScreen(); break;
  }
  lcd.setCursor(19, 3);
  lcd.print(currentScreen + 1);
}
void showEnvironmentScreen() {
  lcd.setCursor(0, 0);
  lcd.print("Environment Data");
  lcd.setCursor(0, 1);
  lcd.print("CO2: ");
  lcd.print(sensors.co2);
  lcd.print(" ppm");
  lcd.setCursor(0, 2);
  lcd.print("Temp: ");
  lcd.print(sensors.temp, 1);
  lcd.print("C  RH:");
  lcd.print(sensors.humidity, 0);
  lcd.print("%");
  lcd.setCursor(0, 3);
  lcd.print("Pressure: ");
  lcd.print(sensors.pressure, 0);
  lcd.print(" hPa");
}
void showSoilScreen() {
  lcd.setCursor(0, 0);
  lcd.print("Soil Moisture");
  lcd.setCursor(0, 1);
  lcd.print("Level: ");
  lcd.print(sensors.soilMoisture);
  lcd.print("%");
  lcd.setCursor(0, 2);
  int bars = map(sensors.soilMoisture, 0, 100, 0, 20);
  for (int i = 0; i < 20; i++) {
    lcd.print(i < bars ? "=" : "-");
  }
  lcd.setCursor(0, 3);
  if (sensors.soilMoisture < 30) lcd.print("Status: DRY");
  else if (sensors.soilMoisture < 70) lcd.print("Status: OK");
  else lcd.print("Status: WET");
}
void showRelayScreen() {
  lcd.setCursor(0, 0);
  lcd.print("Relay Control");
  for (int i = 0; i < 4; i++) {
    int row = 1 + (i / 2);
    int col = (i % 2) * 10;
    lcd.setCursor(col, row);
    lcd.print("R");
    lcd.print(i + 1);
    lcd.print(":");
    lcd.print(digitalRead(relayPins[i]) == LOW ? "ON " : "OFF");
  }
  lcd.setCursor(0, 3);
  lcd.print("Send 1-4 to toggle");
}
void showStartupScreen() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Multi-Sensor System");
  lcd.setCursor(0, 1);
  lcd.print("Starting up...");
  lcd.setCursor(0, 2);
  lcd.print("Please wait...");
}
void sendSerialData() {
  Serial.print("{\"co2\":");
  Serial.print(sensors.co2);
  Serial.print(",\"temp\":");
  Serial.print(sensors.temp);
  Serial.print(",\"humidity\":");
  Serial.print(sensors.humidity);
  Serial.print(",\"pressure\":");
  Serial.print(sensors.pressure);
  Serial.print(",\"soil\":");
  Serial.print(sensors.soilMoisture);
  for (int i = 0; i < 4; i++) {
    Serial.print(",\"relay");
    Serial.print(i + 1);
    Serial.print("\":");
    Serial.print(digitalRead(relayPins[i]) == LOW ? "true" : "false");
  }
  Serial.println("}");
}
void serialEvent() {
  if (Serial.available()) {
    char cmd = Serial.read();
    if (cmd >= '1' && cmd <= '4') {
      int relayIndex = cmd - '1';
      int pin = relayPins[relayIndex];
      digitalWrite(pin, !digitalRead(pin));
      Serial.print("Relay ");
      Serial.print(relayIndex + 1);
      Serial.println(digitalRead(pin) == LOW ? " ON" : " OFF");
      if (currentScreen == 2) updateDisplay();
    }
  }
}