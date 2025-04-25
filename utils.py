# utils.py - v1.1

from datetime import datetime

def log_resolution(coin_id, resolution_type, status):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{coin_id}] Resolution: {resolution_type} | Status: {status}")
