import os
import streamlit as st
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time

try:
    import shap
    shap_available = True
except ImportError:
    shap_available = False

# ============================================================================
# PAGE CONFIGURATION - PREMIUM FINTECH STYLE
# ============================================================================
st.set_page_config(
    page_title="Fraud Detection | Premium AI",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# ============================================================================
# IPHONE-STYLE GLASSMORPHISM UI
# ============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root Colors - Apple iPhone iOS */
    :root {
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --glass-hover: rgba(255, 255, 255, 0.15);
        --text-primary: #FFFFFF;
        --text-secondary: #B0B0B0;
        --success-glow: #34C759;
        --danger-glow: #FF3B30;
        --warning-glow: #FF9500;
        --blur-amount: 15px;
    }
    
    /* Base Styles - Dark Theme */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0f1419 100%);
        color: white;
    }
    
    /* Smooth Page Load Animation */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulseGlow {
        0%, 100% { filter: drop-shadow(0 0 15px rgba(52, 199, 89, 0.3)); transform: scale(1); }
        50% { filter: drop-shadow(0 0 35px rgba(52, 199, 89, 0.7)); transform: scale(1.01); }
    }
    
    @keyframes slideUpFade {
        0% { opacity: 0; transform: translateY(30px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    [data-testid="stAppViewContainer"] {
        animation: fadeIn 0.8s ease-out;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: white;
    }
    
    /* 3D Glass Card */
    .glass-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(var(--blur-amount));
        -webkit-backdrop-filter: blur(var(--blur-amount));
        border-top: 1px solid rgba(255, 255, 255, 0.4);
        border-left: 1px solid rgba(255, 255, 255, 0.2);
        border-right: 1px solid rgba(0, 0, 0, 0.4);
        border-bottom: 1px solid rgba(0, 0, 0, 0.6);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 
            15px 15px 35px rgba(0, 0, 0, 0.5),
            inset 2px 2px 4px rgba(255, 255, 255, 0.2),
            inset -2px -2px 4px rgba(0, 0, 0, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        animation: slideUpFade 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .glass-card:hover {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.04) 100%);
        box-shadow: 
            25px 25px 50px rgba(0, 0, 0, 0.7),
            inset 2px 2px 6px rgba(255, 255, 255, 0.3),
            inset -2px -2px 6px rgba(0, 0, 0, 0.5);
        transform: translateY(-8px) rotateX(4deg) rotateY(-2deg);
    }
    
    /* Header - Glowing Title */
    .premium-header {
        text-align: center;
        margin-bottom: 2.5rem;
        padding: 2.5rem 0;
        font-size: 3.2rem;
        font-weight: 800;
        letter-spacing: -1.5px;
        color: white;
        text-shadow: 0 0 40px rgba(52, 199, 89, 0.3);
        animation: fadeIn 1s ease-out, pulseGlow 4s ease-in-out 1s infinite alternate;
    }
    
    .premium-subheader {
        text-align: center;
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: 2rem;
        font-weight: 400;
        letter-spacing: 0.5px;
        animation: fadeIn 1.2s ease-out;
    }
    
    /* iOS 26 Input Section Styling */
    .input-section-title {
        font-size: 0.85rem;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.65);
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 1rem;
        margin-top: 1.5rem;
        display: flex;
        align-items: center;
        gap: 12px;
        padding-left: 6px;
    }
    
    .input-section-icon {
        font-size: 1.1rem;
        background: rgba(255, 255, 255, 0.08);
        padding: 5px 8px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* 3D Debossed Input Styling */
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select {
        background: rgba(0, 0, 0, 0.2) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        font-size: 1.05rem !important;
        color: white !important;
        transition: all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1) !important;
        font-weight: 500 !important;
        backdrop-filter: blur(40px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
        box-shadow: 
            inset 4px 4px 10px rgba(0, 0, 0, 0.6), 
            inset -2px -2px 6px rgba(255, 255, 255, 0.1),
            0 1px 2px rgba(255, 255, 255, 0.1) !important;
    }
    
    [data-testid="stNumberInput"] input::placeholder,
    [data-testid="stSelectbox"] select::placeholder {
        color: rgba(255, 255, 255, 0.3) !important;
    }
    
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] select:focus {
        background: rgba(0, 0, 0, 0.3) !important;
        box-shadow: 
            inset 6px 6px 14px rgba(0, 0, 0, 0.8), 
            inset -3px -3px 8px rgba(255, 255, 255, 0.15),
            0 0 10px rgba(52, 199, 89, 0.4),
            0 1px 2px rgba(255, 255, 255, 0.2) !important;
        transform: translateY(1px);
    }
    
    /* Dynamic Section Header */
    .section-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: white;
        margin: 3.5rem 0 1.5rem 0;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #FFFFFF 0%, rgba(255,255,255,0.5) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 14px;
        filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
    }
    .section-header::before {
        content: '';
        display: inline-block;
        width: 6px;
        height: 22px;
        background: linear-gradient(180deg, #34C759, #00A86B);
        border-radius: 6px;
        box-shadow: 0 0 12px rgba(52,199,89,0.5);
    }
    
    /* 3D Embossed Button */
    .stButton > button {
        background: linear-gradient(145deg, rgba(60, 215, 100, 1) 0%, rgba(40, 160, 70, 1) 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 32px !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: white !important;
        cursor: pointer !important;
        transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.8px !important;
        min-height: 50px !important;
        box-shadow: 
            0 8px 15px rgba(0, 0, 0, 0.4),
            inset 0 4px 6px rgba(255, 255, 255, 0.4),
            inset 0 -4px 6px rgba(0, 0, 0, 0.2) !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, rgba(70, 230, 110, 1) 0%, rgba(45, 180, 80, 1) 100%) !important;
        box-shadow: 
            0 12px 25px rgba(0, 0, 0, 0.5),
            inset 0 4px 6px rgba(255, 255, 255, 0.5),
            inset 0 -4px 6px rgba(0, 0, 0, 0.3) !important;
        transform: translateY(-4px) scale(1.02) !important;
    }
    
    .stButton > button:active {
        background: linear-gradient(145deg, rgba(40, 160, 70, 1) 0%, rgba(60, 215, 100, 1) 100%) !important;
        transform: translateY(4px) scale(0.98) !important;
        box-shadow: 
            0 2px 5px rgba(0, 0, 0, 0.3),
            inset 0 6px 10px rgba(0, 0, 0, 0.5),
            inset 0 -2px 4px rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Result Card - Safe (Green Glow) */
    .result-safe {
        background: rgba(52, 199, 89, 0.12);
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(52, 199, 89, 0.5);
        border-radius: 24px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 0 50px rgba(52, 199, 89, 0.25),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        animation: glassSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Result Card - Fraud (Red Glow) */
    .result-fraud {
        background: rgba(255, 59, 48, 0.12);
        backdrop-filter: blur(15px);
        border: 1.5px solid rgba(255, 59, 48, 0.5);
        border-radius: 24px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 0 50px rgba(255, 59, 48, 0.25),
                    inset 0 1px 1px rgba(255, 255, 255, 0.1);
        animation: glassSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    @keyframes glassSlideIn {
        0% {
            opacity: 0;
            transform: translateY(40px) scale(0.85);
        }
        60% {
            opacity: 1;
            transform: translateY(-8px) scale(1.04);
        }
        80% {
            transform: translateY(2px) scale(0.98);
        }
        100% {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    /* Badge Styling */
    .badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        margin: 0.75rem 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .badge-safe {
        background: rgba(52, 199, 89, 0.3);
        color: #34C759;
        box-shadow: 0 0 20px rgba(52, 199, 89, 0.3);
    }
    
    .badge-fraud {
        background: rgba(255, 59, 48, 0.3);
        color: #FF3B30;
        box-shadow: 0 0 20px rgba(255, 59, 48, 0.3);
    }
    
    /* 3D Metric Card Layer */
    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-top: 1px solid rgba(255, 255, 255, 0.3);
        border-left: 1px solid rgba(255, 255, 255, 0.1);
        border-right: 1px solid rgba(0, 0, 0, 0.3);
        border-bottom: 1px solid rgba(0, 0, 0, 0.4);
        border-radius: 20px;
        padding: 1.8rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 
            10px 10px 20px rgba(0, 0, 0, 0.4),
            inset 1px 1px 3px rgba(255, 255, 255, 0.2),
            inset -1px -1px 3px rgba(0, 0, 0, 0.2);
        transform-style: preserve-3d;
        perspective: 1000px;
    }
    
    .metric-card:hover {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.04) 100%);
        transform: translateY(-8px) rotateX(5deg) scale(1.03);
        box-shadow: 
            20px 20px 40px rgba(0, 0, 0, 0.5),
            inset 1px 1px 4px rgba(255, 255, 255, 0.3),
            inset -1px -1px 4px rgba(0, 0, 0, 0.3);
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #34C759;
        font-family: 'Inter', sans-serif;
        text-shadow: 0 0 20px rgba(52, 199, 89, 0.3);
    }
    
    .metric-label {
        font-size: 0.8rem;
        color: var(--text-secondary);
        font-weight: 500;
        margin-top: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    
    /* Animated Progress Bar - Glass */
    .progress-container {
        margin: 2rem 0;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: white;
    }
    
    .progress-bar {
        height: 10px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #34C759 0%, #FF3B30 100%);
        border-radius: 10px;
        animation: glowFill 1.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 0 20px rgba(52, 199, 89, 0.5);
    }
    
    @keyframes glowFill {
        0% { width: 0; filter: brightness(1.5); box-shadow: 0 0 30px rgba(52, 199, 89, 0.8); }
        80% { filter: brightness(1.2); box-shadow: 0 0 40px rgba(52, 199, 89, 0.7); }
        100% { width: inherit; filter: brightness(1); box-shadow: 0 0 20px rgba(52, 199, 89, 0.5); }
    }
    
    /* Divider - Subtle Gradient */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        margin: 2rem 0;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.5) 0%, rgba(30, 41, 59, 0.5) 100%);
        backdrop-filter: blur(10px);
    }
    
    .sidebar-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08);
    }
    
    .sidebar-title {
        font-size: 1rem;
        font-weight: 700;
        color: #34C759;
        margin-bottom: 0.75rem;
        text-shadow: 0 0 15px rgba(52, 199, 89, 0.3);
    }
    
    /* Section Header */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        margin: 2.5rem 0 1.5rem 0;
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.3px;
    }
    
    /* Info Box - Glass Alert */
    .info-box {
        background: rgba(52, 199, 89, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(52, 199, 89, 0.3);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        color: var(--text-secondary);
        box-shadow: 0 0 30px rgba(52, 199, 89, 0.1),
                    inset 0 1px 1px rgba(255, 255, 255, 0.08);
    }
    
    /* Text Styling */
    .secondary-text {
        color: var(--text-secondary);
        font-weight: 400;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD MODEL & PREPROCESSORS
# ============================================================================
base_dir = os.path.dirname(__file__)
model_path = os.path.join(base_dir, "model.pkl")
scaler_path = os.path.join(base_dir, "scaler.pkl")
encoders_path = os.path.join(base_dir, "encoder.pkl")
metrics_path = os.path.join(base_dir, "metrics.pkl")

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    with open(scaler_path, "rb") as f:
        scaler = pickle.load(f)
    with open(encoders_path, "rb") as f:
        encoder = pickle.load(f)
        
    # Load metrics dynamically if available
    try:
        with open(metrics_path, "rb") as f:
            model_metrics = pickle.load(f)
    except FileNotFoundError:
        model_metrics = {"Accuracy": "N/A", "Precision": "N/A", "Recall": "N/A", 
                         "F1 Score": "N/A", "ROC AUC": "N/A", "Training Size": "N/A"}
except FileNotFoundError as e:
    st.error(f"Error: Required file not found: {e}")
    st.info("Please ensure train.py has been executed in the backend directory.")
    st.stop()

# ============================================================================
# PREMIUM SIDEBAR - FINTECH STYLE
# ============================================================================
with st.sidebar:
    st.markdown("""
    <div class='sidebar-card'>
        <div class='sidebar-title'>About This Platform</div>
        <p class='secondary-text'>
        Advanced AI-powered fraud detection system using machine learning to protect transactions in real-time.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='sidebar-card'>
        <div class='sidebar-title'>Quick Guide</div>
        <p class='secondary-text'>
        <strong>1.</strong> Enter transaction details<br>
        <strong>2.</strong> Review all information<br>
        <strong>3.</strong> Click Predict button<br>
        <strong>4.</strong> Analyze results & confidence
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Model Stats
    st.markdown("""
    <div class='sidebar-card'>
        <div class='sidebar-title'>Model Metrics (XGBoost)</div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Accuracy", model_metrics.get("Accuracy", "N/A"))
    with col2:
        st.metric("Precision", model_metrics.get("Precision", "N/A"))
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Recall", model_metrics.get("Recall", "N/A"))
    with col2:
        st.metric("F1 Score", model_metrics.get("F1 Score", "N/A"))
    
    st.metric("ROC AUC Score", model_metrics.get("ROC AUC", "N/A"))
    st.metric("Training Size", model_metrics.get("Training Size", "N/A"))
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("""
    <div class='sidebar-card'>
        <div class='sidebar-title'>Portfolio</div>
        <p class='secondary-text'>
        <strong>Built with:</strong> Streamlit, scikit-learn, SHAP<br><br>
        <strong>Model:</strong> XGBoost<br><br>
        <strong>Purpose:</strong> Real-time fraud detection
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# PREMIUM HEADER
# ============================================================================
st.markdown("<div class='premium-header'>Fraud Detection AI</div>", unsafe_allow_html=True)
st.markdown("<div class='premium-subheader'>Advanced machine learning for transaction security</div>", unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ============================================================================
# INPUT SECTION - GLASSMORPHIC CARDS
# ============================================================================
st.markdown("<div class='section-header'>📋 Transaction Details</div>", unsafe_allow_html=True)

# Transaction Information
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='input-section-title'><span class='input-section-icon'>💰</span>Amount & Type</div>", unsafe_allow_html=True)
    
    transaction_amount = st.number_input(
        "Transaction Amount (USD)",
        value=100.0,
        min_value=0.0,
        max_value=100000.0,
        step=10.0,
        key="amount",
        label_visibility="collapsed"
    )
    
    transaction_type = st.selectbox(
        "Transaction Type",
        ["ATM Withdrawal", "Bank Transfer", "Bill Payment", "Online Purchase", "POS Payment"],
        key="type",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<div class='input-section-title'><span class='input-section-icon'>⏰</span>Time & Device</div>", unsafe_allow_html=True)
    
    time_of_transaction = st.slider(
        "Transaction Time (24h format)",
        min_value=0.0,
        max_value=24.0,
        value=12.0,
        step=0.5,
        key="time",
        label_visibility="collapsed"
    )
    
    device_used = st.selectbox(
        "Device Used",
        ["Desktop", "Mobile", "Tablet", "Unknown Device"],
        key="device",
        label_visibility="collapsed"
    )

# Location & Payment
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='input-section-title'><span class='input-section-icon'>📍</span>Location</div>", unsafe_allow_html=True)
    
    location = st.selectbox(
        "Transaction City",
        ["Boston", "Chicago", "Houston", "India", "Los Angeles", "Miami", "New York", "San Francisco", "Seattle"],
        key="location",
        label_visibility="collapsed"
    )

with col2:
    st.markdown("<div class='input-section-title'><span class='input-section-icon'>💳</span>Payment Method</div>", unsafe_allow_html=True)
    
    payment_method = st.selectbox(
        "Payment Method",
        ["Credit Card", "Debit Card", "Invalid Method", "Net Banking", "UPI"],
        key="payment",
        label_visibility="collapsed"
    )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# Account History
st.markdown("<div class='section-header'>📊 Account History</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    previous_fraud = st.number_input(
        "Previous Fraud Incidents",
        value=0,
        min_value=0,
        max_value=100,
        key="prev_fraud",
        label_visibility="collapsed"
    )

with col2:
    account_age = st.number_input(
        "Account Age (days)",
        value=365,
        min_value=0,
        max_value=10000,
        key="account_age",
        label_visibility="collapsed"
    )

with col3:
    transactions_24h = st.number_input(
        "Transactions (24h)",
        value=5,
        min_value=0,
        max_value=500,
        key="trans_24h",
        label_visibility="collapsed"
    )

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ============================================================================
# PREMIUM PREDICT BUTTON
# ============================================================================
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    predict_button = st.button(
        "ANALYZE TRANSACTION",
        use_container_width=True,
        type="primary",
        key="predict_btn"
    )

# ============================================================================
# RESULTS SECTION
# ============================================================================
if predict_button:
    # Loading animation
    with st.spinner("🔍 Analyzing transaction..."):
        time.sleep(0.5)  # Smooth animation
        
        # Prepare features
        features_dict = {
            'Transaction_Amount': transaction_amount,
            'Transaction_Type': transaction_type,
            'Time_of_Transaction': time_of_transaction,
            'Device_Used': device_used,
            'Location': location,
            'Previous_Fraudulent_Transactions': previous_fraud,
            'Account_Age': account_age,
            'Number_of_Transactions_Last_24H': transactions_24h,
            'Payment_Method': payment_method
        }

        features_df = pd.DataFrame([features_dict])

        # Encode
        categorical_cols = ['Transaction_Type', 'Device_Used', 'Location', 'Payment_Method']
        try:
            cat_encoded = pd.DataFrame(
                encoder.transform(features_df[categorical_cols]),
                columns=encoder.get_feature_names_out(categorical_cols)
            )
        except ValueError as e:
            st.error(f"Invalid input: {str(e)}")
            st.stop()

        # Scale
        numerical_cols = ['Transaction_Amount', 'Time_of_Transaction', 'Previous_Fraudulent_Transactions', 
                          'Account_Age', 'Number_of_Transactions_Last_24H']
        num_scaled = pd.DataFrame(scaler.transform(features_df[numerical_cols]), columns=numerical_cols)
        
        # Combine exact format used in train.py (numerical first, then categorical)
        features_df = pd.concat([num_scaled, cat_encoded], axis=1)

        # Predict
        prediction = model.predict(features_df)[0]
        probability = model.predict_proba(features_df)[0][1]

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🎯 Analysis Results</div>", unsafe_allow_html=True)

    # Result Card
    if prediction == 1:
        st.markdown(f"""
        <div class='result-fraud'>
            <h2 style='color: #FF3B30; margin: 0;'>FRAUD ALERT</h2>
            <div class='badge badge-fraud'>High Risk Transaction</div>
            <p style='margin-top: 1rem; color: white;'>This transaction shows patterns consistent with fraudulent activity</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='result-safe'>
            <h2 style='color: #34C759; margin: 0;'>TRANSACTION SAFE</h2>
            <div class='badge badge-safe'>Low Risk</div>
            <p style='margin-top: 1rem; color: white;'>This transaction appears to be legitimate</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Metrics Row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='metric-card'>
            <div class='metric-value'>""" + ("FRAUD" if prediction == 1 else "SAFE") + """</div>
            <div class='metric-label'>Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{probability*100:.1f}%</div>
            <div class='metric-label'>Fraud Risk</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='metric-value'>{max(probability, 1-probability)*100:.1f}%</div>
            <div class='metric-label'>Confidence</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")

    # Animated Progress Bar
    risk_percentage = probability * 100
    st.markdown(f"""
    <div class='progress-container'>
        <div class='progress-label'>
            <span>Fraud Risk Probability</span>
            <span style='color: #34C759; font-weight: 700;'>{risk_percentage:.1f}%</span>
        </div>
        <div class='progress-bar'>
            <div class='progress-fill' style='width: {risk_percentage}%'></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Transaction Summary
    st.markdown("<div class='section-header'>📝 Transaction Summary</div>", unsafe_allow_html=True)
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.markdown(f"""
        <div class='glass-card'>
            <p><strong>Amount:</strong> <span style='color: #34C759;'>${transaction_amount:,.2f}</span></p>
            <p><strong>Type:</strong> {transaction_type}</p>
            <p><strong>Time:</strong> {int(time_of_transaction)}:00</p>
            <p><strong>Device:</strong> {device_used}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown(f"""
        <div class='glass-card'>
            <p><strong>Location:</strong> {location}</p>
            <p><strong>Payment:</strong> {payment_method}</p>
            <p><strong>Account Age:</strong> {account_age} days</p>
            <p><strong>Recent Transactions:</strong> {transactions_24h} in 24h</p>
        </div>
        """, unsafe_allow_html=True)




    # Recommendation
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>💡 Recommendation</div>", unsafe_allow_html=True)
    
    if prediction == 1:
        st.markdown("""
        <div style='background: rgba(255, 59, 48, 0.15); backdrop-filter: blur(10px); border: 1px solid rgba(255, 59, 48, 0.3); border-radius: 16px; padding: 1.5rem; box-shadow: 0 0 30px rgba(255, 59, 48, 0.1);'>
        <strong style='color: #FF3B30;'>BLOCK TRANSACTION</strong> - Request additional verification from customer. Review recent activity patterns.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: rgba(52, 199, 89, 0.15); backdrop-filter: blur(10px); border: 1px solid rgba(52, 199, 89, 0.3); border-radius: 16px; padding: 1.5rem; box-shadow: 0 0 30px rgba(52, 199, 89, 0.1);'>
        <strong style='color: #34C759;'>APPROVE TRANSACTION</strong> - Process normally. Continue monitoring for pattern changes.
        </div>
        """, unsafe_allow_html=True)
