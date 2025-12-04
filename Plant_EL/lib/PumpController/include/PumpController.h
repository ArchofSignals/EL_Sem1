#pragma once
#include <Arduino.h>

class PumpController {
public:
  PumpController(uint8_t relayPin, bool activeLow = true);
  void begin();
  void on();
  void off();
  void pulse(unsigned long ms); // turn on for ms then off (blocking)
  bool isOn();
private:
  uint8_t _pin;
  bool _activeLow;
  bool _state;
};
