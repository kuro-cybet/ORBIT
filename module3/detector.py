import os
import json
import logging
from rules import classify_risk

# ----- Path setup -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

LOG_FILE = os.path.join(RESULTS_DIR, "windows_detection_log.txt")

# ----- Logging setup -----
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
ch = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

# ----- Baseline -----
BASELINE = {"cpu": 50, "memory": 300, "file_access": 10}  # Example baseline

logger.info("OS Level Malware Detection Started")

# ----- Dummy current processes -----
processes = [
    {"name": "unknown.exe", "cpu": 85, "memory": 750, "file_access": 45},
    {"name": "explorer.exe", "cpu": 30, "memory": 200, "file_access": 5},
]

for p in processes:
    # Calculate anomaly score as % deviation from baseline
    cpu_score = ((p["cpu"] - BASELINE["cpu"]) / BASELINE["cpu"]) * 20  # weight 20
    mem_score = ((p["memory"] - BASELINE["memory"]) / BASELINE["memory"]) * 20  # weight 20
    file_score = ((p["file_access"] - BASELINE["file_access"]) / BASELINE["file_access"]) * 10  # weight 10

    anomaly_score = round(max(cpu_score + mem_score + file_score, 0), 2)

    # Determine risk
    risk = classify_risk(anomaly_score)

    # Determine status
    status = "Malicious" if risk == "MALWARE" else "Normal"

    # Log detailed report
    logger.info(f"Status: {status}, Risk Level: {risk},")
    logger.info(f"Anomaly Score: {anomaly_score}, Details: CPU Usage: {p['cpu']}%, Memory Usage: {p['memory']}MB, File Access Count: {p['file_access']}")


