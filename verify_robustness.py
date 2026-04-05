import sys
import os
import json

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

try:
    from api import app, model
    client = app.test_client()

    print("--- Running Robustness Tests ---")

    # Test Case 4: Invalid Payload (Missing required field 'amt')
    print("\nTesting Path 4: Invalid Payload (Missing 'amt')")
    res4 = client.post('/predict', json={
        "trans_date_trans_time": "2026-01-01 12:00:00",
        "lat": 40.0,
        "merch_lat": 40.1
    })
    print(f"Status: {res4.status_code}")
    print(f"Response: {res4.get_json()}")
    assert res4.status_code == 400

    # Test Case 2: Normal Transaction
    print("\nTesting Path 2: Normal Transaction")
    res2 = client.post('/predict', json={
        "amt": 50.0,
        "trans_date_trans_time": "2026-01-01 12:00:00",
        "lat": 40.0,
        "merch_lat": 40.01
    })
    print(f"Status: {res2.status_code}")
    print(f"Response: {res2.get_json()}")
    assert res2.status_code == 200
    assert res2.get_json()['prediction'] == 0

    # Test Case 3: Fraud Transaction (High Amount)
    print("\nTesting Path 3: Fraud Transaction (amt > 3000)")
    res3 = client.post('/predict', json={
        "amt": 5000.0,
        "trans_date_trans_time": "2026-01-01 12:00:00",
        "lat": 40.0,
        "merch_lat": 40.01
    })
    print(f"Status: {res3.status_code}")
    print(f"Response: {res3.get_json()}")
    assert res3.status_code == 200
    assert res3.get_json()['prediction'] == 1

    print("\n--- All Tests Passed! ---")

except Exception as e:
    print(f"\nTest Failed: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
