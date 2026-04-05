import sys
import os

try:
    sys.path.append(r'c:\Users\prashanth\Downloads\fraud\backend')
    from api import app

    client = app.test_client()

    print("Testing /metrics endpoint:")
    metrics_res = client.get('/metrics')
    print("Status:", metrics_res.status_code)
    print("Data:", metrics_res.get_json())
    print("-" * 40)

    print("Testing /predict endpoint:")
    predict_res = client.post('/predict', json={
        'amount': 2500,
        'time': 3,
        'device': 'vpn',
        'location': 'IN',
        'type': 'online_purchase'
    })
    print("Status:", predict_res.status_code)
    print("Data:", predict_res.get_json())
    print("-" * 40)
    
except Exception as e:
    import traceback
    traceback.print_exc()
