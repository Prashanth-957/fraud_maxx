# 💳 Saru Fraud Detection System

A premium, full-stack machine learning-powered fraud detection application built with React, Vite, and XGBoost.

## Quick Start

### 1. Install Dependencies

**Backend (Python):**
```bash
cd backend
pip install -r requirements.txt
pip install flask flask-cors
```

**Frontend (React/Node):**
```bash
cd frontend
npm install
```

### 2. Train the Model (Optional)
If you want to retrain the ML model from scratch on new data:
```bash
cd backend
python train.py
```

Expected output:
- `model.pkl` - Trained XGBoost classification model
- `scaler.pkl` - Feature scaler
- `encoder.pkl` - Categorical encoders
- `metrics.pkl` - Validation scores

### 3. Run the Application

The application requires two separate terminal processes to run simultaneously.

**Terminal 1 (Backend API):**
```bash
cd backend
python api.py
```
*The Flask API will start on port 5000.*

**Terminal 2 (Frontend UI):**
```bash
cd frontend
npm run dev
```
*The React development server will start on port 5173.*

Open your browser to `http://localhost:5173` to view the Saru Dashboard.

## Features

- **Premium 3D-effect UI**: Dynamic glassmorphism interfaces built with Tailwind CSS v4 and Framer Motion.
- **Real-time Fraud Engine**: Connects React inputs seamlessly to your XGBoost backend for instant probability assessments.
- **Engine Analytics**: Dynamic fetched Recharts dashboard comparing live model Accuracy, F1 Scores, and ROC metrics.
- **Role Simulation**: Switch between Analyst, Investigator, and Administrator roles with varying UI permissions.

## File Structure

```
fraud/
├── backend/
│   ├── api.py              # Flask REST Engine endpoint
│   ├── train.py            # Model training script
│   ├── model.pkl           # Trained XGBoost model (generated)
│   ├── scaler.pkl          # Feature scaler (generated)
│   ├── encoder.pkl         # Categorical encoders (generated)
│   └── metrics.pkl         # Performance stats (generated)
├── dataset/
│   └── Fraud.csv           # Training dataset
├── frontend/               # Full Vite + React project
│   ├── src/                
│   │   ├── App.tsx         # Main Saru UI Hub
│   │   ├── index.css       # Global Tailwind theme logic
│   │   └── main.tsx        # React Root
│   ├── package.json        
│   └── vite.config.ts      
└── requirements.txt        # Python dependencies
```
