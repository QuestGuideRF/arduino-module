#define RESET_CLOCK 1
#define DISPLAY_ADDR 0x27
#define DISPLAY_TYPE 1
#define BACKLIGHT 10
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#if (DISPLAY_TYPE == 1)
LiquidCrystal_I2C lcd(DISPLAY_ADDR, 20, 4);
#else
LiquidCrystal_I2C lcd(DISPLAY_ADDR, 16, 2);
#endif
#include "RTClib.h"
RTC_DS3231 rtc;
DateTime now;
unsigned long lastClockUpdate = 0;
const unsigned long clockUpdateInterval = 500;
int8_t hrs, mins, secs;
boolean dotFlag = false;
uint8_t LT[8] = {0b00111, 0b01111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111};
uint8_t UB[8] = {0b11111, 0b11111, 0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000};
uint8_t RT[8] = {0b11100, 0b11110, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111};
uint8_t LL[8] = {0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b01111, 0b00111};
uint8_t LB[8] = {0b00000, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111};
uint8_t LR[8] = {0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11111, 0b11110, 0b11100};
uint8_t UMB[8] = {0b11111, 0b11111, 0b11111, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111};
uint8_t LMB[8] = {0b11111, 0b00000, 0b00000, 0b00000, 0b00000, 0b11111, 0b11111, 0b11111};
void setup() {
  Serial.begin(9600);
  pinMode(BACKLIGHT, OUTPUT);
  analogWrite(BACKLIGHT, 255);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  if (!rtc.begin()) {
    Serial.println("Не удалось найти RTC");
    lcd.setCursor(0, 0);
    lcd.print("RTC ERROR!");
    while (1);
  }
  if (RESET_CLOCK || rtc.lostPower()) {
    Serial.println("Установка времени...");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }
  loadClock();
  now = rtc.now();
  secs = now.second();
  mins = now.minute();
  hrs = now.hour();
  drawClock(hrs, mins, 0, 0, true);
  if (DISPLAY_TYPE == 1) {
    drawDate();
  }
}
void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - lastClockUpdate >= clockUpdateInterval) {
    lastClockUpdate = currentMillis;
    clockTick();
  }
}
void drawDig(byte dig, byte x, byte y) {
  switch (dig) {
    case 0:
      lcd.setCursor(x, y);
      lcd.write(0);
      lcd.write(1);
      lcd.write(2);
      lcd.setCursor(x, y + 1);
      lcd.write(3);
      lcd.write(4);
      lcd.write(5);
      break;
    case 1:
      lcd.setCursor(x + 1, y);
      lcd.write(1);
      lcd.write(2);
      lcd.setCursor(x + 2, y + 1);
      lcd.write(5);
      break;
    case 2:
      lcd.setCursor(x, y);
      lcd.write(6);
      lcd.write(6);
      lcd.write(2);
      lcd.setCursor(x, y + 1);
      lcd.write(3);
      lcd.write(7);
      lcd.write(7);
      break;
    case 3:
      lcd.setCursor(x, y);
      lcd.write(6);
      lcd.write(6);
      lcd.write(2);
      lcd.setCursor(x, y + 1);
      lcd.write(7);
      lcd.write(7);
      lcd.write(5);
      break;
    case 4:
      lcd.setCursor(x, y);
      lcd.write(3);
      lcd.write(4);
      lcd.write(2);
      lcd.setCursor(x + 2, y + 1);
      lcd.write(5);
      break;
    case 5:
      lcd.setCursor(x, y);
      lcd.write(0);
      lcd.write(6);
      lcd.write(6);
      lcd.setCursor(x, y + 1);
      lcd.write(7);
      lcd.write(7);
      lcd.write(5);
      break;
    case 6:
      lcd.setCursor(x, y);
      lcd.write(0);
      lcd.write(6);
      lcd.write(6);
      lcd.setCursor(x, y + 1);
      lcd.write(3);
      lcd.write(7);
      lcd.write(5);
      break;
    case 7:
      lcd.setCursor(x, y);
      lcd.write(1);
      lcd.write(1);
      lcd.write(2);
      lcd.setCursor(x + 1, y + 1);
      lcd.write(0);
      break;
    case 8:
      lcd.setCursor(x, y);
      lcd.write(0);
      lcd.write(6);
      lcd.write(2);
      lcd.setCursor(x, y + 1);
      lcd.write(3);
      lcd.write(7);
      lcd.write(5);
      break;
    case 9:
      lcd.setCursor(x, y);
      lcd.write(0);
      lcd.write(6);
      lcd.write(2);
      lcd.setCursor(x + 1, y + 1);
      lcd.write(4);
      lcd.write(5);
      break;
    case 10:
      lcd.setCursor(x, y);
      lcd.print("   ");
      lcd.setCursor(x, y + 1);
      lcd.print("   ");
      break;
  }
}
void drawDots(byte x, byte y, boolean state) {
  byte code;
  if (state) code = 165;
  else code = 32;
  lcd.setCursor(x, y);
  lcd.write(code);
  lcd.setCursor(x, y + 1);
  lcd.write(code);
}
void drawClock(byte hours, byte minutes, byte x, byte y, boolean dotState) {
  lcd.setCursor(x, y);
  lcd.print("               ");
  lcd.setCursor(x, y + 1);
  lcd.print("               ");
  if (hours / 10 == 0) drawDig(10, x, y);
  else drawDig(hours / 10, x, y);
  drawDig(hours % 10, x + 4, y);
  drawDots(7, y, dotState);
  drawDig(minutes / 10, x + 8, y);
  drawDig(minutes % 10, x + 12, y);
}
void drawDate() {
  lcd.setCursor(0, 3);
  lcd.print("Дата: ");
  if (now.day() < 10) lcd.print("0");
  lcd.print(now.day());
  lcd.print(".");
  if (now.month() < 10) lcd.print("0");
  lcd.print(now.month());
  lcd.print(".");
  lcd.print(now.year());
}
void loadClock() {
  lcd.createChar(0, LT);
  lcd.createChar(1, UB);
  lcd.createChar(2, RT);
  lcd.createChar(3, LL);
  lcd.createChar(4, LB);
  lcd.createChar(5, LR);
  lcd.createChar(6, UMB);
  lcd.createChar(7, LMB);
}
void clockTick() {
  dotFlag = !dotFlag;
  if (dotFlag) {
    secs++;
    if (secs > 59) {
      secs = 0;
      mins++;
      if (mins <= 59) drawClock(hrs, mins, 0, 0, true);
    }
    if (mins > 59) {
      now = rtc.now();
      secs = now.second();
      mins = now.minute();
      hrs = now.hour();
      drawClock(hrs, mins, 0, 0, true);
      if (hrs > 23) {
        hrs = 0;
      }
      if (DISPLAY_TYPE == 1) {
        drawDate();
      }
    }
  }
  drawDots(7, 0, dotFlag);
}