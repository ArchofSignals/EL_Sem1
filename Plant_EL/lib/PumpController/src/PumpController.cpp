#include "PumpController.h"

PumpController::PumpController(uint8_t relayPin, bool activeLow)
  : _pin(relayPin), _activeLow(activeLow), _state(false) {}

void PumpController::begin() {
  pinMode(_pin, OUTPUT);
  off();
}

void PumpController::on() {
  digitalWrite(_pin, _activeLow ? LOW : HIGH);
  _state = true;
}

void PumpController::off() {
  digitalWrite(_pin, _activeLow ? HIGH : LOW);
  _state = false;
}

void PumpController::pulse(unsigned long ms) {
  on();
  delay(ms);
  off();
}

bool PumpController::isOn() {
  return _state;
}
