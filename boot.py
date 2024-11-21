from machine import Pin

# Configure LED pins
led_red = Pin(2, Pin.OUT)  # Red LED on D2
led_blue = Pin(4, Pin.OUT)  # Blue LED on D4
led_green = Pin(5, Pin.OUT)  # Green LED on D5
led_white = Pin(18, Pin.OUT)  # White LED on D18
onboard_led = Pin(2, Pin.OUT)  # Onboard LED (D2 is reused for RED)

# Function to turn off all LEDs
def turn_off_all_leds():
    led_red.value(0)
    led_blue.value(0)
    led_green.value(0)
    led_white.value(0)
    onboard_led.value(0)  # Ensure onboard LED is also OFF

# Initialize all LEDs to OFF state
turn_off_all_leds()
print("All LEDs are OFF at startup")
