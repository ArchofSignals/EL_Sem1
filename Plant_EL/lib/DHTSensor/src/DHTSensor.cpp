#include "DHTSensor.h"

DHTSensor::DHTSensor(uint8_t dataPin, uint8_t type)
 : _dht(dataPin, type), _type(type) {}

void DHTSensor::begin() {
  _dht.begin();
}

float DHTSensor::readTempC() {
  return _dht.readTemperature();
}

float DHTSensor::readHumidity() {
  return _dht.readHumidity();
}

bool DHTSensor::read(float &temp, float &hum) {
  hum = _dht.readHumidity();
  temp = _dht.readTemperature();
  if (isnan(hum) || isnan(temp)) return false;
  return true;
}
