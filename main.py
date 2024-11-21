from umqtt.simple import MQTTClient
from machine import Pin
import time

# MQTT broker details (Raspberry Pi)
MQTT_BROKER = "192.168.1.38"
MQTT_TOPIC = "led/control"

# Configure the LED pins
led_red = Pin(2, Pin.OUT)  # Red LED on D2
led_blue = Pin(4, Pin.OUT)  # Blue LED on D4
led_green = Pin(5, Pin.OUT)  # Green LED on D5
led_white = Pin(18, Pin.OUT)  # White LED on D18

# Turn off all LEDs
def turn_off_all():
    led_red.value(0)
    led_blue.value(0)
    led_green.value(0)
    led_white.value(0)

# Callback for receiving MQTT messages
def mqtt_callback(topic, msg):
    print(f"Received message on {topic.decode()}: {msg.decode()}")
    turn_off_all()  # Turn off all LEDs first
    if msg.decode() == "RED":
        led_red.value(1)  # Turn on Red LED
    elif msg.decode() == "BLUE":
        led_blue.value(1)  # Turn on Blue LED
    elif msg.decode() == "GREEN":
        led_green.value(1)  # Turn on Green LED
    elif msg.decode() == "WHITE":
        led_white.value(1)  # Turn on White LED
    elif msg.decode() == "OFF":
        turn_off_all()  # Turn off all LEDs

# Connect to the MQTT broker
def connect_to_mqtt():
    client = MQTTClient("ESP32", MQTT_BROKER)
    client.set_callback(mqtt_callback)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print(f"Connected to MQTT broker and subscribed to {MQTT_TOPIC}")
    return client

try:
    client = connect_to_mqtt()
    while True:
        client.check_msg()  # Check for new messages
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting...")
    client.disconnect()
    print("Disconnected from MQTT broker.")
