import network
import time
from machine import Pin

# Wi-Fi credentials
WIFI_SSID = "NETGEAR54"
WIFI_PASSWORD = "modernnest392"

# Initialize all LEDs and turn them OFF
def initialize_leds():
    led_red = Pin(21, Pin.OUT)  # Red LED now on D21
    led_blue = Pin(4, Pin.OUT)  # Blue LED on D4
    led_green = Pin(5, Pin.OUT)  # Green LED on D5
    led_white = Pin(18, Pin.OUT)  # White LED on D18

    # Turn OFF all LEDs
    led_red.value(0)
    led_blue.value(0)
    led_green.value(0)
    led_white.value(0)

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print(f"Connecting to Wi-Fi: {WIFI_SSID}...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            print(".", end="")
            time.sleep(1)
    print("\nWi-Fi connected!")
    print("IP address:", wlan.ifconfig()[0])

# Execute on boot
initialize_leds()  # Turn off all LEDs
connect_to_wifi()  # Connect to Wi-Fi
