import sys
import os
import traceback

try:
    sys.path.append(r'c:\Users\prashanth\Downloads\fraud\backend')
    from api import app

    client = app.test_client()

    with open("python_results.txt", "w", encoding="utf-8") as f:
        f.write("Testing /metrics endpoint:\n")
        metrics_res = client.get('/metrics')
        f.write(f"Status: {metrics_res.status_code}\n")
        f.write(f"Data: {metrics_res.get_json()}\n")
        f.write("-" * 40 + "\n")

        f.write("Testing /predict endpoint:\n")
        predict_res = client.post('/predict', json={
            'amount': 2500,
            'time': 3,
            'device': 'vpn',
            'location': 'IN',
            'type': 'online_purchase'
        })
        f.write(f"Status: {predict_res.status_code}\n")
        f.write(f"Data: {predict_res.get_json()}\n")
        f.write("-" * 40 + "\n")
        
except Exception as e:
    with open("python_results.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
