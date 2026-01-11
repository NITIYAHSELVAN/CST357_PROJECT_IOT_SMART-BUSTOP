#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// --- WiFi & GCP Credentials ---
const char* ssid = "cs-mtg-room";      
const char* password = "bilik703"; 
const char* gcpUrl = "https://smartbusstopdatastore-908455702038.asia-southeast1.run.app"; 

// --- Pin Setup ---
#define DHTPIN 27     
#define DHTTYPE DHT11
const int PIR_PIN = 13; 
const int FAN_RELAY_PIN = 26; 
const int LDR_PIN = 34;       
const int LED_NIGHT_PIN = 25; 

// --- Logic Variables ---
bool lastPresence = false;
unsigned long lastHeartbeatTime = 0;
const unsigned long heartbeatInterval = 3000; 

// --- Fan Timer Variables ---
unsigned long fanStartTime = 0;
bool fanIsRunning = false;
const unsigned long fanDuration = 10000; // 10 seconds

DHT dht(DHTPIN, DHTTYPE);

// --- Function to Send Data to GCP ---
void sendToGCP(float t, float h, bool p, int l) {
  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(gcpUrl);
    http.setTimeout(400); 
    http.addHeader("Content-Type", "application/json");

    String lightStatus = (l > 2500) ? "Night" : "Day";
    
    // Updated: Uses the timer state for the cloud status
    String fanStatus = fanIsRunning ? "ON" : "OFF";

    String json = "{";
    json += "\"temp\":" + String(t) + ",";
    json += "\"hum\":" + String(h) + ",";
    json += "\"presence\":" + String(p ? "true" : "false") + ",";
    json += "\"ldr\":" + String(l) + ",";
    json += "\"light_mode\":\"" + lightStatus + "\",";
    json += "\"fan_mode\":\"" + fanStatus + "\"";
    json += "}";

    int httpResponseCode = http.POST(json);
    Serial.print("Cloud Sync Status: "); Serial.println(httpResponseCode);
    http.end();
  }
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(PIR_PIN, INPUT);
  pinMode(FAN_RELAY_PIN, OUTPUT);
  pinMode(LED_NIGHT_PIN, OUTPUT);
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { 
    delay(500); 
    Serial.print("."); 
  }
  Serial.println("\n--- WiFi Connected ---");
}

void loop() {
  // 1. READ SENSORS
  int ldrVal = analogRead(LDR_PIN);
  bool currentPresence = (digitalRead(PIR_PIN) == HIGH);
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  // 2. INSTANT LOCAL ACTION
  // Night Light Control
  digitalWrite(LED_NIGHT_PIN, ldrVal > 2500 ? HIGH : LOW);

  // --- SMART FAN TIMER LOGIC ---
  // Trigger condition: Presence AND Temp >= 29
  if (currentPresence && t >= 29.0) {
    if (!fanIsRunning) {
      Serial.println(">>> Fan Triggered: On for 10s");
      fanIsRunning = true;
      fanStartTime = millis();
      digitalWrite(FAN_RELAY_PIN, HIGH);
      sendToGCP(t, h, currentPresence, ldrVal); // Update cloud immediately
    }
  }

  // Check if timer should stop
  if (fanIsRunning && (millis() - fanStartTime >= fanDuration)) {
    Serial.println(">>> Timer finished: Fan Off");
    fanIsRunning = false;
    digitalWrite(FAN_RELAY_PIN, LOW);
    sendToGCP(t, h, currentPresence, ldrVal); // Update cloud immediately
  }

  // 3. EVENT-BASED CLOUD LOGIC (Presence change)
  if (currentPresence != lastPresence) {
    lastPresence = currentPresence; 
    sendToGCP(t, h, currentPresence, ldrVal);
    lastHeartbeatTime = millis();
  }

  // 4. HEARTBEAT SYNC
  if (millis() - lastHeartbeatTime >= heartbeatInterval) {
    sendToGCP(t, h, currentPresence, ldrVal);
    lastHeartbeatTime = millis();
  }

  delay(10); 
}