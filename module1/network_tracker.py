import psutil
import time
from datetime import datetime
from module1.event_stream import EventStream


class NetworkTracker:
    def __init__(self, poll_interval=1):
        self.poll_interval = poll_interval
        self.prev_connections = set()
        self.stream = EventStream()
        self.connection_metadata = {}  # Track connection start times

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def snapshot(self):
        conns = set()
        for c in psutil.net_connections(kind="inet"):
            if c.pid and c.raddr:
                conns.add((c.pid, c.laddr.ip, c.laddr.port,
                           c.raddr.ip, c.raddr.port))
        return conns
    
    def get_current_connections(self):
        """Get current network connections with metadata for UI display"""
        connections = []
        try:
            for c in psutil.net_connections(kind="inet"):
                if c.raddr:  # Only external connections
                    try:
                        process_name = psutil.Process(c.pid).name() if c.pid else "unknown"
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_name = "unknown"
                    
                    conn_key = f"{c.laddr.ip}:{c.laddr.port}-{c.raddr.ip}:{c.raddr.port}"
                    
                    # Track connection start time
                    if conn_key not in self.connection_metadata:
                        self.connection_metadata[conn_key] = {
                            'start_time': time.time(),
                            'bytes': 0
                        }
                    
                    duration = int(time.time() - self.connection_metadata[conn_key]['start_time'])
                    
                    connections.append({
                        'pid': c.pid or 0,
                        'process': process_name,
                        'proto': 'TCP' if c.type == 1 else 'UDP',
                        'local': f"{c.laddr.ip}:{c.laddr.port}",
                        'remote': f"{c.raddr.ip}:{c.raddr.port}",
                        'remote_ip': c.raddr.ip,
                        'remote_port': c.raddr.port,
                        'state': c.status,
                        'duration': f"{duration}s",
                        'bytes': f"{self.connection_metadata[conn_key]['bytes']} KB"
                    })
        except Exception as e:
            print(f"Error getting connections: {e}")
        
        return connections
    
    def get_event_stream(self):
        """Expose event stream for UI consumption"""
        return self.stream

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

