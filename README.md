README for CHROMA Senior Design Project
Welcome to the CHROMA Senior Design Project repository! This project aims to develop an adaptive lighting system for photographers, optimizing photo quality for diverse skin tones using RGB LED lightboxes controlled by ESP32 microcontrollers. This README provides an overview of the repository structure, key components, and how to get started.

Repository Structure
boot.py
Configures the ESP32 microcontroller to automatically connect to the local Wi-Fi network on startup and initialize the LED pins.

Initializes GPIO pins for Red, Green, Blue, and White LEDs.
Establishes a Wi-Fi connection using the specified SSID and password.
Key Features:
Ensures LEDs are off upon boot.
Automatically connects the ESP32 to the preconfigured Wi-Fi network.
main.py
Handles the primary operations of the ESP32 microcontroller, including subscribing to MQTT topics and controlling LED lightboxes.
Functionality Includes:

Listens for MQTT messages from the Raspberry Pi (acting as the broker).
Parses incoming messages to control specific LED channels (e.g., Red, Green, Blue, White).
Supports commands to turn on/off individual LEDs or all LEDs simultaneously.
mqtt_publisher.py
A Python script designed for the Raspberry Pi to act as the central hub for communication and lighting adjustments.
Capabilities:

Publishes MQTT messages to control the LED strips on the ESP32 devices.
Sends commands to adjust brightness, color temperature, or specific RGB settings for the lightboxes.
Includes GUI components to manually override automatic settings.
Getting Started
Wi-Fi Configuration (ESP32):
Update the boot.py file with your Wi-Fi network’s SSID and password:

python
Copy code
WIFI_SSID = "YourWiFiSSID"
WIFI_PASSWORD = "YourWiFiPassword"
The ESP32 will use these credentials to automatically connect upon startup.

MQTT Broker Setup (Raspberry Pi):
Ensure the Raspberry Pi is running an MQTT broker such as Mosquitto. The broker facilitates communication between the Raspberry Pi and the ESP32 devices.

Deploying Code:

Upload boot.py and main.py to your ESP32 microcontroller.
Place mqtt_publisher.py on the Raspberry Pi.
Controlling LEDs:

The mqtt_publisher.py script allows you to send commands to the ESP32 to control the LEDs.
Commands are structured to include individual or collective LED adjustments (e.g., RED_ON, ALL_OFF).
Example Commands
Below are sample commands that the Raspberry Pi can send via MQTT to control the LEDs:

Turn Red LED On:
RED_ON
Turn Red LED Off:
RED_OFF
Turn All LEDs Off:
ALL_OFF
Future Features
Integration of RGBWW (Warm and Cool White) lighting adjustments for finer control over color temperature.
Implementation of sliders for brightness and temperature adjustments via the Raspberry Pi GUI.
Expansion to control three lightboxes for professional photography setups.
For more details or questions, feel free to contact the development team. Happy coding!
