import threading
from module1.process_tracker import ProcessTracker

def start_process_monitor():
    """
    Starts the process tracker in a background thread.
    """
    print("[Module 1] ORBIT Real-Time Monitoring Started")
    
    # Initialize tracker with a reasonable poll interval
    process_tracker = ProcessTracker(poll_interval=1.0)
    
    # Start tracking in a daemon thread so it closes when main app closes
    t = threading.Thread(target=process_tracker.track, daemon=True)
    t.start()

# Only for standalone testing
if __name__ == "__main__":
    start_process_monitor()
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping monitor...")
