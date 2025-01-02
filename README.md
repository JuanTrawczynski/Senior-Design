# **CHROMA Senior Design Project**
Welcome to the **CHROMA Senior Design Project** repository! This project aims to develop an adaptive lighting system for photographers, optimizing photo quality for diverse skin tones using RGB LED lightboxes controlled by ESP32 microcontrollers. This README provides an overview of the repository structure, key components, and how to get started.

# **Repository Structure**

**boot.py**
- Description: Configures the ESP32 microcontroller to automatically connect to the local Wi-Fi network on startup and initialize the LED pins.
- Key Features:
	- Initializes GPIO pins for Red, Green, Blue, and White LEDs.
	- Establishes a Wi-Fi connection using the specified SSID and password.
	- Ensures LEDs are off upon boot.
	- Automatically connects the ESP32 to the preconfigured Wi-Fi network.

**main.py**
- Description: Handles the primary operations of the ESP32 microcontroller, including subscribing to MQTT topics and controlling LED lightboxes.
- Functionality Includes:
	- Listens for MQTT messages from the Raspberry Pi (acting as the broker).
	- Parses incoming messages to control specific LED channels (e.g., Red, Green, Blue, White).
	- Supports commands to turn on/off individual LEDs or all LEDs simultaneously.

**mqtt_publisher.py**
- Description: A Python script designed for the Raspberry Pi to act as the central hub for communication and lighting adjustments.
- Capabilities:
	- Publishes MQTT messages to control the LED strips on the ESP32 devices.
	- Sends commands to adjust brightness, color temperature, or specific RGB settings for the lightboxes.
	- Includes GUI components to manually override automatic settings.

