import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt

# MQTT broker details
BROKER = "192.168.1.38"  # Replace with your Raspberry Pi IP
TOPIC = "led/control"

# Initialize MQTT client
client = mqtt.Client()
is_connected = False

# Functions for MQTT communication
def connect_esp32():
    global is_connected
    try:
        client.connect(BROKER)
        is_connected = True
        update_status("Connected to ESP32")
    except Exception as e:
        update_status("Failed to connect: " + str(e))

def disconnect_esp32():
    global is_connected
    try:
        client.disconnect()
        is_connected = False
        update_status("Disconnected from ESP32")
    except Exception as e:
        update_status("Failed to disconnect: " + str(e))

def toggle_led():
    if not is_connected:
        messagebox.showwarning("Warning", "ESP32 is not connected!")
        return

    try:
        # Send "ON" and "OFF" messages alternately
        client.publish(TOPIC, "ON")
        messagebox.showinfo("Success", "Toggled LED ON!")
    except Exception as e:
        update_status("Failed to send message: " + str(e))

# Update GUI status
def update_status(message):
    status_label.config(text=f"Status: {message}")

# GUI setup
def setup_gui():
    window = tk.Tk()
    window.title("ESP32 LED Controller")

    # Status Label
    global status_label
    status_label = tk.Label(window, text="Status: Disconnected", font=("Arial", 12))
    status_label.pack(pady=10)

    # Buttons
    connect_button = tk.Button(window, text="Connect to ESP32", font=("Arial", 12), command=connect_esp32)
    connect_button.pack(pady=5)

    disconnect_button = tk.Button(window, text="Disconnect ESP32", font=("Arial", 12), command=disconnect_esp32)
    disconnect_button.pack(pady=5)

    toggle_button = tk.Button(window, text="Toggle LED", font=("Arial", 12), command=toggle_led)
    toggle_button.pack(pady=5)

    # Run the GUI
    window.mainloop()

# Main program
if __name__ == "__main__":
    setup_gui()
