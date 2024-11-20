import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "192.168.1.38"  # Replace with your Raspberry Pi IP
TOPIC = "led/control"

# Initialize variables
client = mqtt.Client()
is_connected = False
led_state = False  # Keeps track of LED state (ON/OFF)

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

def toggle_led():
    global led_state
    if not is_connected:
        messagebox.showwarning("Warning", "ESP32 is not connected!")
        return

    try:
        # Toggle LED state
        if led_state:
            client.publish(TOPIC, "OFF")  # Turn LED OFF
            messagebox.showinfo("Success", "LED Turned OFF!")
        else:
            client.publish(TOPIC, "ON")  # Turn LED ON
            messagebox.showinfo("Success", "LED Turned ON!")
        led_state = not led_state  # Update LED state
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
    root.title("Test Connection GUI")

    # Status Label
    status_label = tk.Label(root, text="Status: Disconnected", font=("Arial", 12))
    status_label.pack(pady=10)

    # Buttons
    connect_button = tk.Button(root, text="Connect to ESP32", font=("Arial", 12), command=connect_esp32)
    connect_button.pack(pady=5)

    disconnect_button = tk.Button(root, text="Disconnect ESP32", font=("Arial", 12), command=disconnect_esp32)
    disconnect_button.pack(pady=5)

    toggle_button = tk.Button(root, text="LED Toggle", font=("Arial", 12), command=toggle_led)
    toggle_button.pack(pady=5)

    # Start real-time status monitoring
    check_connection()

    # Run the GUI
    root.mainloop()

# Main program
if __name__ == "__main__":
    setup_gui()
