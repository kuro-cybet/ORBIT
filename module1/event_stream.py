import json
import os

# Use absolute path relative to this file to ensure 'output' directory is always found in module1
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "live_events.json")
MAX_EVENTS = 500


class EventStream:
    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        if not os.path.exists(OUTPUT_FILE):
            with open(OUTPUT_FILE, "w") as f:
                json.dump([], f)

    def push(self, event):
        # Read existing data
        data = []
        if os.path.exists(OUTPUT_FILE):
            try:
                with open(OUTPUT_FILE, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                data = []

        # Append new event
        data.append(event)

        # Truncate if needed
        if len(data) > MAX_EVENTS:
            data = data[-MAX_EVENTS:]

        # Write back atomically (or just overwrite)
        try:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError as e:
            print(f"Error writing to event stream: {e}")
