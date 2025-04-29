
from datetime import datetime

def log_resolution(coin_id, resolution_type, status):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{coin_id}] Resolution: {resolution_type} | Status: {status}")

def format_duration(seconds):
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    return f"{int(days)} Days {int(hours)} Hours {int(minutes)} Minutes"
