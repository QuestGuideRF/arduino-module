#include <Wire.h>
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27, 20, 4);
String inputString = "";
boolean stringComplete = false;
void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("FITODOMIK");
  lcd.setCursor(0, 1);
  lcd.print("WAITING FOR DATA...");
  inputString.reserve(100);
}
void loop() {
  if (stringComplete) {
    parseAndDisplay(inputString);
    inputString = "";
    stringComplete = false;
  }
}
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}
void parseAndDisplay(String data) {
  int firstSeparator = data.indexOf('|');
  int secondSeparator = data.indexOf('|', firstSeparator + 1);
  if (firstSeparator > 0 && secondSeparator > firstSeparator) {
    String thresholds = data.substring(0, firstSeparator);
    String devices = data.substring(firstSeparator + 1, secondSeparator);
    String schedule = data.substring(secondSeparator + 1);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("THRESHOLDS: ");
    lcd.print(thresholds);
    lcd.setCursor(0, 1);
    lcd.print("DEVICES: ");
    lcd.print(devices);
    lcd.setCursor(0, 2);
    lcd.print("SCHEDULE:");
    lcd.setCursor(0, 3);
    lcd.print(schedule);
  }
}