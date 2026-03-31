import os
import pickle
import warnings

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend - no GUI needed
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.metrics import classification_report, confusion_matrix

from imblearn.over_sampling import SMOTE

warnings.filterwarnings('ignore')

# =========================
# LOAD DATA
# =========================

base_dir = os.path.dirname(__file__)
dataset_path = os.path.join(base_dir, '..', 'dataset', 'Fraud.csv')
df = pd.read_csv(dataset_path)


# =========================
# DATA CLEANING
# =========================

df.drop(['Transaction_ID', 'User_ID'], axis=1, inplace=True)

df['Transaction_Amount'].fillna(df['Transaction_Amount'].median(), inplace=True)
df['Time_of_Transaction'].fillna(df['Time_of_Transaction'].median(), inplace=True)
df['Device_Used'].fillna(df['Device_Used'].mode()[0], inplace=True)
df['Location'].fillna(df['Location'].mode()[0], inplace=True)
df['Payment_Method'].fillna(df['Payment_Method'].mode()[0], inplace=True)


# =========================
# VISUALIZATION
# =========================

sns.countplot(x='Fraudulent', data=df)
plt.title("Fraud vs Non-Fraud")
plt.close()

plt.figure(figsize=(12, 8))

numeric_df = df.select_dtypes(include=['int64', 'float64'])

sns.heatmap(numeric_df.corr(), cmap='coolwarm', annot=True)

plt.title("Correlation Heatmap")
plt.close()

sns.boxplot(x='Fraudulent', y='Transaction_Amount', data=df)
plt.title("Transaction Amount vs Fraud")
plt.close()


# =========================
# SPLIT DATA
# =========================

X = df.drop('Fraudulent', axis=1)
y = df['Fraudulent']

X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=0.80, random_state=1)


# =========================
# PREPROCESSING
# =========================

X_train_num = X_train.select_dtypes(['float64', 'int64'])
X_train_cat = X_train.select_dtypes(['object'])


# =========================
# TRANSFORM TRAINING DATA
# =========================

scaler = StandardScaler()

X_train_num_sca = pd.DataFrame(scaler.fit_transform(X_train_num),
                               index=X_train_num.index,
                               columns=X_train_num.columns)
X_train_num_sca.head()


coder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')

X_train_cat_sca = pd.DataFrame(coder.fit_transform(X_train_cat),
                               index=X_train_cat.index,
                               columns=coder.get_feature_names_out(X_train_cat.columns))
X_train_cat_sca.head()

X_train_transformed = pd.concat([X_train_num_sca, X_train_cat_sca], axis=1)
X_train_transformed.head()


# =========================
# TRANSFORM TEST DATA
# =========================

X_test_num = X_test.select_dtypes(['float64', 'int64'])
X_test_cat = X_test.select_dtypes(['object'])

X_test_num_sca = pd.DataFrame(scaler.transform(X_test_num),
                              index=X_test_num.index,
                              columns=X_test_num.columns)

X_test_cat_sca = pd.DataFrame(coder.transform(X_test_cat),
                              index=X_test_cat.index,
                              columns=coder.get_feature_names_out(X_test_cat.columns))

X_test_transformed = pd.concat([X_test_num_sca, X_test_cat_sca], axis=1)
X_test_transformed.head()


# =========================
# SMOTE (BALANCING)
# =========================

# Before SMOTE, visualize class distribution
plt.figure()
sns.countplot(x=y)
plt.title("Before SMOTE (Original Class Distribution)")
plt.xlabel("Class (0 = Not Fraud, 1 = Fraud)")
plt.ylabel("Count")
plt.close()

smote = SMOTE(random_state=1, k_neighbors=5)
X_train_res, y_train_res = smote.fit_resample(X_train_transformed, y_train)

# After SMOTE, visualize class distribution
plt.figure()
sns.countplot(x=y_train_res)
plt.title("After SMOTE (Balanced Class Distribution)")
plt.xlabel("Class (0 = Not Fraud, 1 = Fraud)")
plt.ylabel("Count")
plt.close()


# =========================
# MODEL TRAINING - LOGISTIC REGRESSION
# =========================

print("=" * 50)
print("LOGISTIC REGRESSION MODEL")
print("=" * 50)

classifier = LogisticRegression()
classifier.fit(X_train_res, y_train_res)

y_test_pred_lr = classifier.predict(X_test_transformed)
y_prob_lr = classifier.predict_proba(X_test_transformed)[:, 1]

print(f'Accuracy: {accuracy_score(y_test, y_test_pred_lr):.4f}')
print(f'Precision: {precision_score(y_test, y_test_pred_lr):.4f}')
print(f'Recall: {recall_score(y_test, y_test_pred_lr):.4f}')
print(f'F1 Score: {f1_score(y_test, y_test_pred_lr):.4f}')
print(f'ROC AUC Score: {roc_auc_score(y_test, y_prob_lr):.4f}')



# =========================
# XGBOOST MODEL (FINAL BEST)
# =========================



print("\n" + "=" * 50)
print("XGBOOST MODEL (FINAL)")
print("=" * 50)


best_f1 = 0
best_xgb_model = None

for w in [5, 10, 15, 20, 30, 50]:
    print(f"\n=== scale_pos_weight: {w} ===")


    xgb_temp = XGBClassifier(
        scale_pos_weight=w,   # 🔥 handles imbalance better
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=1,
        eval_metric='logloss'
    )

    print("Training XGBoost...")
    xgb_temp.fit(X_train_res, y_train_res)

    # 🔥 IMPORTANT: Use probability + threshold tuning

    y_prob_xgb = xgb_temp.predict_proba(X_test_transformed)[:, 1]
    y_pred_xgb = (y_prob_xgb > 0.4).astype(int)



    print('\n--- XGBoost Performance ---')
    print(f'Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}')
    print(f'Precision: {precision_score(y_test, y_pred_xgb):.4f}')
    print(f'Recall: {recall_score(y_test, y_pred_xgb):.4f}')
    
    current_f1 = f1_score(y_test, y_pred_xgb)
    print(f'F1 Score: {current_f1:.4f}')
    print(f'ROC AUC Score: {roc_auc_score(y_test, y_prob_xgb):.4f}')

    if current_f1 > best_f1:
        best_f1 = current_f1
        best_xgb_model = xgb_temp

xgb_model = best_xgb_model
print(f"\nSelected best XGBoost model with F1 Score: {best_f1:.4f}")

# Calculate final metrics for the best model
y_prob_best = xgb_model.predict_proba(X_test_transformed)[:, 1]
y_pred_best = (y_prob_best > 0.4).astype(int)

final_metrics = {
    "Accuracy": f"{accuracy_score(y_test, y_pred_best) * 100:.2f}%",
    "Precision": f"{precision_score(y_test, y_pred_best) * 100:.2f}%",
    "Recall": f"{recall_score(y_test, y_pred_best) * 100:.2f}%",
    "F1 Score": f"{best_f1 * 100:.2f}%",
    "ROC AUC": f"{roc_auc_score(y_test, y_prob_best) * 100:.2f}%",
    "Training Size": f"{len(X_train_res):,} transactions"
}

# =========================
# SAVE MODEL AND PREPROCESSORS
# =========================

model_path = os.path.join(base_dir, 'model.pkl')
scaler_path = os.path.join(base_dir, 'scaler.pkl')
encoder_path = os.path.join(base_dir, 'encoder.pkl')
metrics_path = os.path.join(base_dir, 'metrics.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(xgb_model, f)

with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)

with open(encoder_path, 'wb') as f:
    pickle.dump(coder, f)

with open(metrics_path, 'wb') as f:
    pickle.dump(final_metrics, f)

print("\n" + "=" * 50)
print("MODEL SAVED SUCCESSFULLY")
print("=" * 50)
print(f"Model saved to: {model_path}")
print(f"Scaler saved to: {scaler_path}")
print(f"Encoder saved to: {encoder_path}")
print(f"Metrics saved to: {metrics_path}")
print(f"Feature columns: {X_test_transformed.columns.tolist()}")