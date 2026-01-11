# 🚍 Smart Bus Stop IoT System

**Course:** CST357 - IoT Architecture & Smart Applications  
**University:** Universiti Sains Malaysia (USM)  


## 📖 Project Overview
The **Smart Bus Stop IoT System** is an intelligent urban infrastructure solution designed to address energy waste and improve passenger comfort. By integrating an **ESP32 microcontroller** with environmental sensors and **Google Cloud Platform (GCP)**, this system automates cooling and lighting facilities based on real-time needs rather than continuous "always-on" operation.

This project directly aligns with **SDG 11 (Sustainable Cities)** and **SDG 7 (Clean Energy)** by optimizing resource usage in public spaces.

### ✨ Key Features
* **Automated Cooling:** The fan activates *only* when a passenger is detected AND the temperature exceeds 29°C.
* **Smart Lighting:** Night lights turn on automatically when ambient light drops below a specific threshold (Night Mode).
* **Cloud Integration:** Real-time data streaming to **Google Cloud Run** and **Firestore**.
* **Live Dashboard:** A web-based driver dashboard showing occupancy status and environmental data.
* **Analytics:** Integration with **ThingsBoard** for historical data visualization.

---

## 📂 Repository Structure

| File | Description |
| :--- | :--- |
| `HTTPPOST.ino` | **Arduino Code:** Main firmware for the ESP32. Handles sensor reading, local automation logic, and HTTP POST requests. |
| `main.py` | **Cloud Function:** Python script hosted on Google Cloud Run. Processes incoming data, logs it to Firestore, and serves the HTML Dashboard. |
| `requirement.txt` | **Dependencies:** Python libraries required for the Cloud Run environment. |

---

## 🛠️ Hardware Requirements

* **Microcontroller:** NodeMCU ESP32
* **Sensors:**
    * DHT11 (Temperature & Humidity)
    * HC-SR501 (PIR Motion Sensor)
    * LDR Module (Light Dependent Resistor)
* **Actuators:**
    * DC Motor + Fan Blade
    * 5V Relay Module (to control the fan)
    * LED Module (Night Light)
* **Power:** USB Cable / Battery Pack

### 🔌 Wiring Diagram (Pinout)

| Component | ESP32 Pin | Description |
| :--- | :--- | :--- |
| **DHT11 Data** | `D27` | Temperature Sensor Input |
| **PIR Output** | `D13` | Motion Sensor Input |
| **LDR Analog** | `D34` | Light Sensor Input |
| **Relay Signal** | `D26` | Controls Fan Motor |
| **LED (+)** | `D25` | Controls Night Light |

---

## 💻 Software Dependencies

### 1. Arduino IDE (for ESP32)
Ensure you have the **ESP32 Board Manager** installed. You will need the following libraries:
* `WiFi.h` (Built-in)
* `HTTPClient.h` (Built-in)
* `DHT Sensor Library` by Adafruit

### 2. Google Cloud Platform (Python 3.10+)
The `main.py` script requires the following packages (listed in `requirement.txt`):
* `functions-framework==3.*`
* `google-cloud-firestore`
* `requests`

---

## 🚀 Setup & Installation Guide

### Step 1: Cloud Configuration (GCP)
1.  Create a **Google Cloud Project**.
2.  Enable **Cloud Run** and **Firestore** APIs.
3.  Deploy `main.py` and `requirement.txt` to a Cloud Run function.
4.  **Important:** Update the `TB_ACCESS_TOKEN` in `main.py` with your own ThingsBoard token if replicating the analytics.
5.  Copy your Cloud Run **Service URL**.

### Step 2: Hardware Configuration
1.  Connect all sensors and actuators to the ESP32 according to the **Wiring Diagram** above.
2.  Open `HTTPPOST.ino` in the Arduino IDE.
3.  **Update Credentials:**
    * Change `ssid` and `password` to your local Wi-Fi credentials.
    * Paste your Cloud Run URL into the `gcpUrl` variable:
        ```cpp
        const char* gcpUrl = "[https://YOUR-CLOUD-RUN-URL.run.app](https://YOUR-CLOUD-RUN-URL.run.app)";
        ```
4.  Upload the code to the ESP32.

### Step 3: Analytics
1.  Create an account on **ThingsBoard.cloud**.
2.  Create a new Device and copy its **Access Token**.
3.  Paste this token into the `main.py` file on the cloud server.

---

## 📊 Usage

1.  **Power on** the ESP32.
2.  The device will connect to Wi-Fi and begin transmitting data.
3.  **Triggering the Fan:** Wave your hand in front of the PIR sensor (simulating a passenger) and ensure the sensor is warm (>29°C).
4.  **View Dashboard:** Open your Cloud Run URL in a web browser to see the **Live Driver Dashboard**.

---

## 🌍 SDG Impact

This project supports **UN Sustainable Development Goal 11 (Sustainable Cities and Communities)** by creating a smarter, safer public transport environment. It reduces the carbon footprint of public utilities through presence-based automation, ensuring energy is only consumed when necessary.

---

**Project Team:**

* Nitiyah Selvan A/L P.Suresh
* Muhammad Arif Hakimi Bin Shamsul Hisham


<img width="900" height="695" alt="0" src="https://github.com/user-attachments/assets/86c05df1-e220-4eb1-89c3-c30a678c9483" />
<img width="1600" height="884" alt="0 (4)" src="https://github.com/user-attachments/assets/d8dd862f-05dc-49e7-8c52-eff6cbc34d8d" />
<img width="1600" height="898" alt="0 (3)" src="https://github.com/user-attachments/assets/5336aaa5-9899-4974-add5-0837941bb9db" />
<img width="1919" height="1079" alt="0 (2)" src="https://github.com/user-attachments/assets/9eda9f44-a4d9-4d0e-b1c6-f2653f9013b1" />
<img width="1600" height="779" alt="0 (1)" src="https://github.com/user-attachments/assets/15bd94bd-3443-4d09-88cd-43f146734501" />
