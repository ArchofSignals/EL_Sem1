#pragma once
#include <Arduino.h>
#include <DHT.h>

class DHTSensor {
public:
  DHTSensor(uint8_t dataPin, uint8_t type = DHT11);
  void begin();
  float readTempC();
  float readHumidity();
  bool read(float &temp, float &hum); // returns success
private:
  DHT _dht;
  uint8_t _type;
};
