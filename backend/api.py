import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from geopy.distance import geodesic
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "online",
        "message": "Saru API is running. Use /predict or /metrics endpoints."
    }), 200

# ============================================================================
# LOAD MODEL & PREPROCESSORS
# ============================================================================
base_dir = os.path.dirname(__file__)

def load_artifact(name):
    path = os.path.join(base_dir, f"{name}.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    print(f"Warning: {name}.pkl not found.")
    return None

print("Loading ML Assets...")
model = load_artifact("model")
scaler = load_artifact("scaler")
le_gender = load_artifact("label_encoder_gender")
best_thresh = load_artifact("best_threshold")
feature_names = load_artifact("feature_names")

merchant_fraud_rate = load_artifact("merchant_fraud_rate") or {}
merchant_count = load_artifact("merchant_count") or {}
category_fraud_rate = load_artifact("category_fraud_rate") or {}
job_fraud_rate = load_artifact("job_fraud_rate") or {}

if not best_thresh:
    best_thresh = 0.5

print("Assets loaded successfully.")

# ============================================================================
# VALIDATION MODELS
# ============================================================================
class TransactionPayload(BaseModel):
    amt: float
    trans_date_trans_time: str
    lat: float
    long: Optional[float] = 0.0
    merch_lat: float
    merch_long: Optional[float] = 0.0
    zip: Optional[int] = 0
    city_pop: Optional[int] = 0
    gender: Optional[str] = "M"
    dob: Optional[str] = "1990-01-01"
    merchant: Optional[str] = ""
    category: Optional[str] = ""
    job: Optional[str] = ""

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Step 1: Check if assets are loaded properly (Path 1)
        if model is None or scaler is None or feature_names is None:
            return jsonify({
                "error": "ML assets not loaded properly. Wait for training to complete.",
                "detail": "ML assets not loaded properly..."
            }), 500

        # Step 2: Validate input payload (Path 4)
        try:
            data = request.get_json(force=True)
            payload = TransactionPayload(**data)
        except (ValidationError, Exception) as e:
            return jsonify({
                "error": "Invalid input payload",
                "detail": str(e)
            }), 400

        # Extract values
        amt = payload.amt
        lat = payload.lat
        long = payload.long
        merch_lat = payload.merch_lat
        merch_long = payload.merch_long
        trans_date = payload.trans_date_trans_time
        
        # Feature Engineering
        trans_dt = pd.to_datetime(trans_date)
        hour = trans_dt.hour
        day_of_week = trans_dt.dayofweek
        month = trans_dt.month
        
        # Distance
        try:
            distance = geodesic((lat, long), (merch_lat, merch_long)).km
        except:
            # Fallback simple distance calculation if requested
            distance = abs(lat - merch_lat) * 111 # Roughly 111km per degree
            
        # Age
        age = 2026 - pd.to_datetime(payload.dob).year
        
        # Step 3: Handle normal transactions and fraud (Paths 2 & 3)
        # Use simple rules as a deterministic baseline (as per user instructions)
        rule_flagged = False
        rule_explanation = ""
        
        if amt > 3000 or hour < 6 or distance > 50:
            rule_flagged = True
            rule_explanation = "High amount, late night, or extreme distance flagged by rules"

        # ML Model Prediction
        m_fraud_rate = merchant_fraud_rate.get(payload.merchant, 0)
        m_count = merchant_count.get(payload.merchant, 0)
        c_fraud_rate = category_fraud_rate.get(payload.category, 0)
        j_fraud_rate = job_fraud_rate.get(payload.job, 0)
        
        try:
            encoded_gender = le_gender.transform([payload.gender])[0]
        except:
            encoded_gender = 1

        features_dict = {
            'amt': amt,
            'zip': payload.zip,
            'city_pop_log': np.log1p(payload.city_pop),
            'hour': hour,
            'day_of_week': day_of_week,
            'month': month,
            'distance': distance,
            'age': age,
            'merchant_fraud_rate': m_fraud_rate,
            'merchant_count': m_count,
            'category_fraud_rate': c_fraud_rate,
            'job_fraud_rate': j_fraud_rate,
            'gender': encoded_gender
        }
        
        row = {f: 0 for f in feature_names}
        for k, v in features_dict.items():
            if k in row:
                row[k] = v

        features_df = pd.DataFrame([row])[feature_names]
        scaled_features = scaler.transform(features_df)
        probability = float(model.predict_proba(scaled_features)[0][1])
        
        # Combine Rule-based and ML prediction
        prediction = 1 if (probability > best_thresh or rule_flagged) else 0
        
        # Explanations
        explanations = []
        if rule_flagged:
            explanations.append(rule_explanation)
            
        if amt > 1000:
            explanations.append(f"Unusually high transaction amount (${float(amt):.2f}).")
        if hour < 5 or hour > 23:
            explanations.append(f"Late night transaction flagged at {hour}:00 hours.")
        if distance > 250:
            explanations.append(f"Extreme distance from typical area ({int(distance)}km).")
        elif distance > 50:
            explanations.append(f"Moderate distance anomaly ({int(distance)}km).")
            
        if not explanations:
            explanations.append("Transaction characteristics appear normal")

        return jsonify({
            "prediction": prediction,
            "probability": probability,
            "explanation": explanations,
            "threshold": float(best_thresh)
        })

    except Exception as e:
        # Step 4: Global try/except (return 400 for unexpected errors)
        traceback.print_exc()
        return jsonify({"error": "Unexpected error", "detail": str(e)}), 400

        return jsonify({
            "prediction": prediction,
            "probability": probability,
            "explanation": explanations,
            "threshold": float(best_thresh)
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

@app.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = load_artifact("metrics")
    if metrics:
        return jsonify(metrics)
    return jsonify({
        "Accuracy": "N/A", "Precision": "N/A", "Recall": "N/A", 
        "F1 Score": "N/A", "ROC AUC": "N/A", "Training Size": "N/A"
    }), 404

# if __name__ == '__main__':
#     print("Starting Saru API Server on port 5000...")
#     app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Saru API Server on port {port}...")
    app.run(host='0.0.0.0', port=port)
