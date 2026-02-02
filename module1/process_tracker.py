import psutil
import time
from datetime import datetime
from module1.event_stream import EventStream


class ProcessTracker:
    def __init__(self, poll_interval=1):
        self.poll_interval = poll_interval
        self.prev_pids = set(psutil.pids())
        self.stream = EventStream()

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def track(self):
        while True:
            current_pids = set(psutil.pids())

            # New processes
            for pid in current_pids - self.prev_pids:
                self.process_start(pid)

            # Terminated processes
            for pid in self.prev_pids - current_pids:
                self.process_terminate(pid)

            self.prev_pids = current_pids
            time.sleep(self.poll_interval)

    def process_start(self, pid):
        try:
            proc = psutil.Process(pid)
            # Fetch name immediately to avoid race conditions if process dies
            process_name = proc.name()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return

        event = {
            "timestamp": self.timestamp(),
            "pid": pid,
            "process": process_name,
            "event": "process_start"
        }
        self.stream.push(event)
        # print(event)  # Commented out for production cleanliness

    def process_terminate(self, pid):
        event = {
            "timestamp": self.timestamp(),
            "pid": pid,
            "process": "unknown",
            "event": "process_terminate"
        }
        self.stream.push(event)
        # print(event)  # Commented out for production cleanliness
