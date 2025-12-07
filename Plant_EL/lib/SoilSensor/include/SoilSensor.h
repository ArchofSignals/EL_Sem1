#pragma once
#include <Arduino.h>

class SoilSensor {
public:
  // pin: ADC pin (e.g., 34)
  SoilSensor(uint8_t adcPin, int dryADC = 3000, int wetADC = 1200);
  void begin();               // call in setup if needed
  int readRaw();              // returns raw ADC (0..4095)
  int readPercent();          // mapped percent 0..100 (0=wet,100=dry)
  void calibrate(int dryVal, int wetVal);
private:
  uint8_t _adcPin;
  int _dryADC;
  int _wetADC;
};
