import os
import pickle
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from geopy.distance import geodesic
from datasets import load_dataset

from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, average_precision_score)
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import make_pipeline as make_imblearn_pipeline
import optuna

warnings.filterwarnings('ignore')

# =========================
# 1. LOAD DATA (Hugging Face)
# =========================
print("Loading dataset...")
dataset = load_dataset("NeerajCodz/creditCardFraudDetection")
train_data = dataset['train'].to_pandas()
test_data = dataset['test'].to_pandas()

# Downsample negative class heavily to prevent SMOTE OOM error
pos_train = train_data[train_data['is_fraud'] == 1]
neg_train = train_data[train_data['is_fraud'] == 0].sample(n=len(pos_train) * 5, random_state=42)
train_data = pd.concat([pos_train, neg_train]).sample(frac=1.0, random_state=42).reset_index(drop=True)

pos_test = test_data[test_data['is_fraud'] == 1]
neg_test = test_data[test_data['is_fraud'] == 0].sample(n=len(pos_test) * 5, random_state=42)
test_data = pd.concat([pos_test, neg_test]).sample(frac=1.0, random_state=42).reset_index(drop=True)

print(f"Train shape: {train_data.shape}, Test shape: {test_data.shape}")

# =========================
# 2. INITIAL CLEANING
# =========================
cols_to_drop = ['street', 'city', 'state', 'first', 'last', 'Unnamed: 0', 'trans_num']
train_data.drop(cols_to_drop, axis=1, inplace=True, errors='ignore')
test_data.drop(cols_to_drop, axis=1, inplace=True, errors='ignore')

# =========================
# 3. FEATURE ENGINEERING
# =========================
for df in [train_data, test_data]:
    df["trans_date_trans_time"] = pd.to_datetime(df["trans_date_trans_time"])
    df["hour"] = df["trans_date_trans_time"].dt.hour
    df["day_of_week"] = df["trans_date_trans_time"].dt.dayofweek
    df["month"] = df["trans_date_trans_time"].dt.month
    df.drop("trans_date_trans_time", axis=1, inplace=True)

def compute_distance(row):
    try:
        return geodesic((row['lat'], row['long']), (row['merch_lat'], row['merch_long'])).km
    except:
        return np.nan

for df in [train_data, test_data]:
    df['distance'] = df.apply(compute_distance, axis=1)

current_year = 2026
for df in [train_data, test_data]:
    df['age'] = current_year - pd.to_datetime(df['dob']).dt.year

loc_cols = ['cc_num', 'lat', 'long', 'merch_lat', 'merch_long', 'dob']
train_data.drop(loc_cols, axis=1, inplace=True, errors='ignore')
test_data.drop(loc_cols, axis=1, inplace=True, errors='ignore')

for df in [train_data, test_data]:
    df['city_pop_log'] = np.log1p(df['city_pop'])
    df.drop('city_pop', axis=1, inplace=True)

# =========================
# 4. TARGET LEAKAGE SAFE AGGREGATIONS (use only train data)
# =========================
merchant_fraud_rate_train = train_data.groupby('merchant')['is_fraud'].mean()
train_data['merchant_fraud_rate'] = train_data['merchant'].map(merchant_fraud_rate_train)
test_data['merchant_fraud_rate'] = test_data['merchant'].map(merchant_fraud_rate_train).fillna(0)

merchant_count_train = train_data['merchant'].value_counts()
train_data['merchant_count'] = train_data['merchant'].map(merchant_count_train)
test_data['merchant_count'] = test_data['merchant'].map(merchant_count_train).fillna(0)

train_data['merchant_category'] = train_data['merchant'] + '_' + train_data['category']
test_data['merchant_category'] = test_data['merchant'] + '_' + test_data['category']
train_data.drop('merchant', axis=1, inplace=True)
test_data.drop('merchant', axis=1, inplace=True)

category_fraud_rate_train = train_data.groupby('category')['is_fraud'].mean()
train_data['category_fraud_rate'] = train_data['category'].map(category_fraud_rate_train)
test_data['category_fraud_rate'] = test_data['category'].map(category_fraud_rate_train).fillna(0)

job_fraud_rate_train = train_data.groupby('job')['is_fraud'].mean()
train_data['job_fraud_rate'] = train_data['job'].map(job_fraud_rate_train)
test_data['job_fraud_rate'] = test_data['job'].map(job_fraud_rate_train).fillna(0)

train_data.drop(['merchant_category', 'job', 'category'], axis=1, inplace=True)
test_data.drop(['merchant_category', 'job', 'category'], axis=1, inplace=True)

# =========================
# 5. ENCODE CATEGORICAL VARIABLES
# =========================
le_gender = LabelEncoder()
train_data['gender'] = le_gender.fit_transform(train_data['gender'])
test_data['gender'] = le_gender.transform(test_data['gender'])

cat_cols = train_data.select_dtypes(include=['object']).columns.tolist()
if cat_cols:
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded_train = encoder.fit_transform(train_data[cat_cols])
    encoded_test = encoder.transform(test_data[cat_cols])
    feat_names = encoder.get_feature_names_out(cat_cols)
    train_data = pd.concat([train_data.drop(cat_cols, axis=1),
                            pd.DataFrame(encoded_train, columns=feat_names, index=train_data.index)], axis=1)
    test_data = pd.concat([test_data.drop(cat_cols, axis=1),
                           pd.DataFrame(encoded_test, columns=feat_names, index=test_data.index)], axis=1)

for df in [train_data, test_data]:
    if 'unix_time' in df.columns:
        df.drop('unix_time', axis=1, inplace=True)

# =========================
# 6. SEPARATE FEATURES AND TARGET
# =========================
X_train_raw = train_data.drop('is_fraud', axis=1)
y_train_raw = train_data['is_fraud']
X_test_raw = test_data.drop('is_fraud', axis=1)
y_test_raw = test_data['is_fraud']

# =========================
# 7. SCALING (fit only on training)
# =========================
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_raw)
X_test_scaled = scaler.transform(X_test_raw)

# =========================
# 8. BASELINE LOGISTIC REGRESSION
# =========================
print("\n" + "="*50)
print("BASELINE: LOGISTIC REGRESSION (class_weight='balanced')")
print("="*50)
lr = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
lr.fit(X_train_scaled, y_train_raw)
y_prob_lr = lr.predict_proba(X_test_scaled)[:, 1]
auc_pr_lr = average_precision_score(y_test_raw, y_prob_lr)
print(f"AUC-PR: {auc_pr_lr:.4f}")
if auc_pr_lr < 0.10:
    print("⚠️  WARNING: Very weak signal. Check data quality.")
else:
    print("Baseline shows meaningful signal. Proceeding with XGBoost.")

# =========================
# 9. OPTUNA TUNING (with SMOTE inside CV)
# =========================
def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 30, 100),
        'max_depth': trial.suggest_int('max_depth', 4, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.1, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'gamma': trial.suggest_float('gamma', 0, 5),
        'reg_alpha': trial.suggest_float('reg_alpha', 0, 5),
        'reg_lambda': trial.suggest_float('reg_lambda', 0, 5),
        'eval_metric': 'aucpr',
        'tree_method': 'hist',
        'random_state': 42,
        'verbosity': 0
    }
    model = XGBClassifier(**params)
    pipeline = make_imblearn_pipeline(SMOTE(random_state=42, k_neighbors=5), model)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    scores = cross_val_score(pipeline, X_train_scaled, y_train_raw,
                             cv=cv, scoring='average_precision')
    return scores.mean()

print("\n" + "="*50)
print("OPTUNA TUNING (3-fold CV with SMOTE inside)")
print("="*50)
study = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=42))
study.optimize(objective, n_trials=5, show_progress_bar=True)
best_params = study.best_params
print("\nBest parameters:", best_params)

# =========================
# 10. TRAIN FINAL MODEL WITH SMOTE ON FULL TRAINING SET
# =========================
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train_raw)

best_params['eval_metric'] = 'aucpr'
best_params['tree_method'] = 'hist'
best_params['random_state'] = 42
best_params['verbosity'] = 0

xgb_final = XGBClassifier(**best_params)
xgb_final.fit(X_train_res, y_train_res, verbose=False)

# =========================
# 11. THRESHOLD OPTIMIZATION (using validation split)
# =========================
X_train_sub, X_val, y_train_sub, y_val = train_test_split(
    X_train_res, y_train_res, test_size=0.2, random_state=42, stratify=y_train_res
)
xgb_temp = XGBClassifier(**best_params)
xgb_temp.fit(X_train_sub, y_train_sub, verbose=False)
y_prob_val = xgb_temp.predict_proba(X_val)[:, 1]

thresholds = np.arange(0.05, 0.95, 0.01)
best_f1 = 0
best_thresh = 0.5
for t in thresholds:
    y_pred_val = (y_prob_val > t).astype(int)
    f1 = f1_score(y_val, y_pred_val)
    if f1 > best_f1:
        best_f1 = f1
        best_thresh = t

# Final test predictions
y_prob_test = xgb_final.predict_proba(X_test_scaled)[:, 1]
y_pred_test = (y_prob_test > best_thresh).astype(int)

# =========================
# 12. FINAL METRICS
# =========================
final_metrics = {
    "Accuracy": f"{accuracy_score(y_test_raw, y_pred_test)*100:.2f}%",
    "Precision": f"{precision_score(y_test_raw, y_pred_test)*100:.2f}%",
    "Recall": f"{recall_score(y_test_raw, y_pred_test)*100:.2f}%",
    "F1 Score": f"{f1_score(y_test_raw, y_pred_test)*100:.2f}%",
    "ROC AUC": f"{roc_auc_score(y_test_raw, y_prob_test)*100:.2f}%",
    "AUC-PR": f"{average_precision_score(y_test_raw, y_prob_test)*100:.2f}%",
    "Best Threshold": f"{best_thresh:.2f}",
    "Training Size (after SMOTE)": f"{len(X_train_res):,}"
}

print("\n" + "="*50)
print("FINAL MODEL PERFORMANCE")
print("="*50)
for k, v in final_metrics.items():
    print(f"{k}: {v}")

# =========================
# 13. SAVE ARTIFACTS
# =========================
base_dir = os.path.dirname(os.path.abspath("__file__"))  # adjust as needed
artifacts = {
    'model': xgb_final,
    'scaler': scaler,
    'label_encoder_gender': le_gender,
    'onehot_encoder': encoder if cat_cols else None,
    'best_threshold': best_thresh,
    'metrics': final_metrics,
    'feature_names': X_train_raw.columns.tolist(),
    'merchant_fraud_rate': merchant_fraud_rate_train.to_dict(),
    'merchant_count': merchant_count_train.to_dict(),
    'category_fraud_rate': category_fraud_rate_train.to_dict(),
    'job_fraud_rate': job_fraud_rate_train.to_dict()
}

for name, obj in artifacts.items():
    if obj is not None:
        with open(os.path.join(base_dir, f'{name}.pkl'), 'wb') as f:
            pickle.dump(obj, f)

print("\n✓ All artifacts saved successfully.")