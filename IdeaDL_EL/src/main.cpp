#include <Wire.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>

// --- WIFI CONFIG ---
const char* ssid = "Octadex Prime";
const char* password = "meitantei@2060";

// --- MQTT CONFIG ---
// Use your laptop's local IP address (e.g., 192.168.1.5)
const char* mqtt_server = "192.168.70.79"; 
const int mqtt_port = 1883;
const char* mqtt_topic = "sensor/vibration";

// --- OBJECTS ---
WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    
    // Attempt to connect
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Init Sensor
  if(!accel.begin()) {
    Serial.println("No ADXL345 detected");
    while(1);
  }
  accel.setRange(ADXL345_RANGE_16_G);
  
  // Setup Network
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  // Ensure MQTT connection is alive
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Read Sensor
  sensors_event_t event; 
  accel.getEvent(&event);

  // formatting payload: "x,y,z"
  // Example Output: "0.12,0.55,9.81"
  String payload = String(event.acceleration.x) + "," + 
                   String(event.acceleration.y) + "," + 
                   String(event.acceleration.z);

  // Publish to topic
  // c_str() converts the String object to a C-style string required by the library
  client.publish(mqtt_topic, payload.c_str());

  // Delay dictates sampling rate. 
  // 10ms delay + execution time ~= approx 50-80Hz depending on network
  delay(10); 
}