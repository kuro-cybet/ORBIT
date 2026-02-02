import psutil
import time
from datetime import datetime
from module1.event_stream import EventStream


class NetworkTracker:
    def __init__(self, poll_interval=1):
        self.poll_interval = poll_interval
        self.prev_connections = set()
        self.stream = EventStream()

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def snapshot(self):
        conns = set()
        for c in psutil.net_connections(kind="inet"):
            if c.pid and c.raddr:
                conns.add((c.pid, c.laddr.ip, c.laddr.port,
                           c.raddr.ip, c.raddr.port))
        return conns

    def track(self):
        self.prev_connections = self.snapshot()
        while True:
            current = self.snapshot()
            new_conns = current - self.prev_connections

            for conn in new_conns:
                self.new_connection(conn)

            self.prev_connections = current
            time.sleep(self.poll_interval)

    def new_connection(self, conn):
        pid, lip, lport, rip, rport = conn
        try:
            pname = psutil.Process(pid).name()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pname = "unknown"

        event = {
            "timestamp": self.timestamp(),
            "pid": pid,
            "process": pname,
            "event": "network_connect",
            "details": f"{rip}:{rport}"
        }

        self.stream.push(event)
        print(event)
