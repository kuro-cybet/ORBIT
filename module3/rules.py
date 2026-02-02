# rules.py

def classify_risk(score):
    """
    Classify the risk based on deviation score.
    """
    if score >= 0.7:
        return "MALWARE"
    elif score >= 0.4:
        return "SUSPICIOUS"
    else:
        return "NORMAL"
