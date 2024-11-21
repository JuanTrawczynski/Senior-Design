import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "192.168.1.38"  # Replace with your Raspberry Pi IP
TOPIC = "led/control"

# Initialize variables
client = mqtt.Client()
is_connected = False

# LED states
led_states = {
    "RED": False,
    "BLUE": False,
    "GREEN": False,
    "WHITE": False,
}

# Functions for MQTT communication
def connect_esp32():
    global is_connected
    try:
        client.connect(BROKER)
        is_connected = True
        update_status("Connected to ESP32")
    except Exception as e:
        update_status(f"Failed to connect: {str(e)}")

def disconnect_esp32():
    global is_connected
    try:
        client.disconnect()
        is_connected = False
        update_status("Disconnected from ESP32")
    except Exception as e:
        update_status(f"Failed to disconnect: {str(e)}")

def toggle_led(color):
    if not is_connected:
        messagebox.showwarning("Warning", "ESP32 is not connected!")
        return

    try:
        # Determine ON or OFF command
        if led_states[color]:
            client.publish(TOPIC, f"{color}_OFF")
            led_states[color] = False
            update_status(f"Turned {color} OFF")
        else:
            client.publish(TOPIC, f"{color}_ON")
            led_states[color] = True
            update_status(f"Turned {color} ON")
    except Exception as e:
        update_status(f"Failed to send message: {str(e)}")

# Update GUI status
def update_status(message):
    status_label.config(text=f"Status: {message}")

# Real-time status monitoring
def check_connection():
    if is_connected:
        status_label.config(text="Status: Connected to ESP32")
    else:
        status_label.config(text="Status: Disconnected")
    # Call this function again after 1 second
    root.after(1000, check_connection)

# GUI setup
def setup_gui():
    global root, status_label
    root = tk.Tk()
    root.title("LED Debugger GUI")

    # Status Label
    status_label = tk.Label(root, text="Status: Disconnected", font=("Arial", 12))
    status_label.pack(pady=10)

    # Buttons for connecting and disconnecting
    connect_button = tk.Button(root, text="Connect to ESP32", font=("Arial", 12), command=connect_esp32)
    connect_button.pack(pady=5)

    disconnect_button = tk.Button(root, text="Disconnect ESP32", font=("Arial", 12), command=disconnect_esp32)
    disconnect_button.pack(pady=5)

    # Buttons for toggling individual LEDs
    red_button = tk.Button(root, text="Toggle Red", font=("Arial", 12), command=lambda: toggle_led("RED"))
    red_button.pack(pady=5)

    green_button = tk.Button(root, text="Toggle Green", font=("Arial", 12), command=lambda: toggle_led("GREEN"))
    green_button.pack(pady=5)

    blue_button = tk.Button(root, text="Toggle Blue", font=("Arial", 12), command=lambda: toggle_led("BLUE"))
    blue_button.pack(pady=5)

    white_button = tk.Button(root, text="Toggle White", font=("Arial", 12), command=lambda: toggle_led("WHITE"))
    white_button.pack(pady=5)

    # Start real-time status monitoring
    check_connection()

    # Run the GUI
    root.mainloop()

# Main program
if __name__ == "__main__":
    setup_gui()
