# anomaly_score.py

def calculate_anomaly_score(cpu, memory, baseline):
    """
    Calculate deviation score based on CPU and memory usage compared to baseline.
    """
    score = 0.0

    if cpu > baseline["cpu"]:
        score += 0.5
    if memory > baseline["memory"]:
        score += 0.4

    return round(score, 2)


