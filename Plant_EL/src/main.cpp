#include <Arduino.h>
#include "SoilSensor.h"
#include "DHTSensor.h"
#include "PumpController.h"
#include <WiFi.h>
#include <HTTPClient.h>

// pins
constexpr uint8_t PIN_DHT = 4;
constexpr uint8_t PIN_SOIL = 34;
constexpr uint8_t PIN_RELAY = 26;

// instances
SoilSensor soil(PIN_SOIL, 3000, 1200);
DHTSensor dht(PIN_DHT, DHT11);
PumpController pump(PIN_RELAY, true);

// thresholds
const int WATER_THRESHOLD = 30; // percent dry -> water
const unsigned long READ_INTERVAL = 30000;
const unsigned long PUMP_MS = 5000;

unsigned long lastRead = 0;

void setup() {
  Serial.begin(115200);
  soil.begin();
  dht.begin();
  pump.begin();

  // WiFi connect — replace with your credentials or manage a separate WiFi module/class
  WiFi.begin("SSID", "PASSWORD");
  Serial.print("Connecting WiFi.");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void sendData(float t, float h, int raw, int pct) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  http.begin("http://172.17.1.86:5000/data");
  http.addHeader("Content-Type", "application/json");
  String payload = "{\"temperature\":" + String(t,1) + ",";
  payload += "\"humidity\":" + String(h,1) + ",";
  payload += "\"soil_adc\":" + String(raw) + ",";
  payload += "\"soil_percent\":" + String(pct) + "}";
  int code = http.POST(payload);
  Serial.printf("POST => %d\n", code);
  http.end();
}

void loop() {
  unsigned long now = millis();
  if (now - lastRead >= READ_INTERVAL) {
    lastRead = now;
    float t,h;
    bool ok = dht.read(t,h);
    if (!ok) {
      Serial.println("DHT read failed");
    }
    int raw = soil.readRaw();
    int pct = soil.readPercent();
    Serial.printf("T: %.1f H: %.1f SoilRaw: %d SoilPct: %d\n", t,h,raw,pct);

    sendData(t,h,raw,pct);

    if (pct > WATER_THRESHOLD) {
      Serial.println("Soil dry -> Pumping");
      pump.pulse(PUMP_MS); // blocking; OK for simple apps
    }
  }
}
