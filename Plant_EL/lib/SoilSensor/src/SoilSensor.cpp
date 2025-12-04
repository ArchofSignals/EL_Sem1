#include "SoilSensor.h"

SoilSensor::SoilSensor(uint8_t adcPin, int dryADC, int wetADC)
  : _adcPin(adcPin), _dryADC(dryADC), _wetADC(wetADC) {}

void SoilSensor::begin() {
  // nothing for ADC-only pins, but keep API consistent
  // analogReadResolution(12); // ESP32 default is 12-bit (0..4095)
}

int SoilSensor::readRaw() {
  // ADC1 pins (32-39) are input-only on some modules; ensure correct pin
  int val = analogRead(_adcPin);
  return val;
}

int SoilSensor::readPercent() {
  int raw = readRaw();
  float pct = 100.0f * (float)(raw - _wetADC) / (float)(_dryADC - _wetADC);
  if (pct < 0) pct = 0;
  if (pct > 100) pct = 100;
  return (int)round(pct);
}

void SoilSensor::calibrate(int dryVal, int wetVal) {
  _dryADC = dryVal;
  _wetADC = wetVal;
}
