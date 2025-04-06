import requests

WLED_IP = "192.168.1.48"

print("=== WLED Preset Toggler ===")
print("Enter preset number (1-5) to toggle WLED preset.")
print("Enter 'q' to quit.\n")

while True:
    user_input = input("Preset (1-5): ").strip()

    if user_input.lower() == "q":
        print("Exiting.")
        break

    if user_input in {"1", "2", "3", "4", "5"}:
        preset = int(user_input)
        url = f"http://{WLED_IP}/win&PL={preset}"
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                print(f"Activated preset {preset}")
            else:
                print(f"Failed to activate preset {preset}. HTTP {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Invalid input. Please enter 1-5 or 'q'.")
