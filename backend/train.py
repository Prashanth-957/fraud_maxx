import os
import pickle
import warnings

import numpy as np
import pandas as pd
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
plt.show()

plt.figure(figsize=(12, 8))

numeric_df = df.select_dtypes(include=['int64', 'float64'])

sns.heatmap(numeric_df.corr(), cmap='coolwarm', annot=True)

plt.title("Correlation Heatmap")
plt.show()

sns.boxplot(x='Fraudulent', y='Transaction_Amount', data=df)
plt.title("Transaction Amount vs Fraud")
plt.show()


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


coder = OneHotEncoder(drop='first', sparse_output=False)

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
plt.show()

smote = SMOTE(random_state=1, k_neighbors=5)
X_train_res, y_train_res = smote.fit_resample(X_train_transformed, y_train)

# After SMOTE, visualize class distribution
plt.figure()
sns.countplot(x=y_train_res)
plt.title("After SMOTE (Balanced Class Distribution)")
plt.xlabel("Class (0 = Not Fraud, 1 = Fraud)")
plt.ylabel("Count")
plt.show()


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
# MODEL TRAINING - RANDOM FOREST
# =========================

print("\n" + "=" * 50)
print("RANDOM FOREST MODEL (BASELINE)")
print("=" * 50)

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=10,
    random_state=1
)

model.fit(X_train_res, y_train_res)

y_pred = model.predict(X_test_transformed)
y_prob = model.predict_proba(X_test_transformed)[:, 1]

print(f'Accuracy: {accuracy_score(y_test, y_pred):.4f}')
print(f'Precision: {precision_score(y_test, y_pred):.4f}')
print(f'Recall: {recall_score(y_test, y_pred):.4f}')
print(f'F1 Score: {f1_score(y_test, y_pred):.4f}')
print(f'ROC AUC Score: {roc_auc_score(y_test, y_prob):.4f}')

metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
values = [
    accuracy_score(y_test, y_pred),
    precision_score(y_test, y_pred),
    recall_score(y_test, y_pred),
    f1_score(y_test, y_pred)
]

plt.figure(figsize=(10, 6))
plt.bar(metrics, values)
plt.title("Random Forest Performance (Baseline)")
plt.ylim(0, 1)
plt.ylabel("Score")
plt.show()


# =========================
# MODEL OPTIMIZATION WITH RANDOMIZED SEARCH
# =========================

print("\n" + "=" * 50)
print("RANDOM FOREST MODEL (OPTIMIZED)")
print("=" * 50)


# Initialize the Random Forest Classifier
rf = RandomForestClassifier(
    random_state=1,
    class_weight='balanced'
)

param_dist = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5],
    'min_samples_leaf': [1, 2],
    'bootstrap': [True, False]
}

# Instantiate RandomizedSearchCV
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_dist,
    n_iter=10,
    scoring='f1',
    cv=3,
    verbose=1,
    random_state=1,
    n_jobs=-1
)

# Fit the RandomizedSearchCV object to the resampled training data
print("Starting RandomizedSearchCV...")
random_search.fit(X_train_res, y_train_res)

# Print the best parameters found
print("\nBest Parameters found by RandomizedSearchCV:")
print(random_search.best_params_)

# Get the best model from the search
best_rf = random_search.best_estimator_

# Make predictions with the optimized model
y_pred_optimized = best_rf.predict(X_test_transformed)
y_prob_optimized = best_rf.predict_proba(X_test_transformed)[:, 1]

# Print evaluation metrics
print('\n--- Optimized Random Forest Performance ---')
print(f'Accuracy: {accuracy_score(y_test, y_pred_optimized):.4f}')
print(f'Precision: {precision_score(y_test, y_pred_optimized):.4f}')
print(f'Recall: {recall_score(y_test, y_pred_optimized):.4f}')
print(f'F1 Score: {f1_score(y_test, y_pred_optimized):.4f}')
print(f'ROC AUC Score: {roc_auc_score(y_test, y_prob_optimized):.4f}')

# Visualize optimized model performance
metrics_optimized = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
values_optimized = [
    accuracy_score(y_test, y_pred_optimized),
    precision_score(y_test, y_pred_optimized),
    recall_score(y_test, y_pred_optimized),
    f1_score(y_test, y_pred_optimized)
]

plt.figure(figsize=(10, 6))
plt.bar(metrics_optimized, values_optimized)
plt.title("Random Forest Performance (Optimized)")
plt.ylim(0, 1)
plt.ylabel("Score")
plt.show()


# =========================
# XGBOOST MODEL (FINAL BEST)
# =========================



print("\n" + "=" * 50)
print("XGBOOST MODEL (FINAL)")
print("=" * 50)


for w in [5, 10, 15, 20, 30, 50]:
    print(f"\n=== scale_pos_weight: {w} ===")


    xgb_model = XGBClassifier(
        scale_pos_weight=w,   # 🔥 handles imbalance better
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        random_state=1,
        use_label_encoder=False,
        eval_metric='logloss'
    )

    print("Training XGBoost...")
    xgb_model.fit(X_train_res, y_train_res)

    # 🔥 IMPORTANT: Use probability + threshold tuning

    y_prob_xgb = xgb_model.predict_proba(X_test_transformed)[:, 1]
    y_pred_xgb = (y_prob_xgb > 0.4).astype(int)



    print('\n--- XGBoost Performance ---')
    print(f'Accuracy: {accuracy_score(y_test, y_pred_xgb):.4f}')
    print(f'Precision: {precision_score(y_test, y_pred_xgb):.4f}')
    print(f'Recall: {recall_score(y_test, y_pred_xgb):.4f}')
    print(f'F1 Score: {f1_score(y_test, y_pred_xgb):.4f}')
    print(f'ROC AUC Score: {roc_auc_score(y_test, y_prob_xgb):.4f}')



# =========================
# SAVE MODEL AND PREPROCESSORS
# =========================

model_path = os.path.join(base_dir, 'model.pkl')
scaler_path = os.path.join(base_dir, 'scaler.pkl')
encoder_path = os.path.join(base_dir, 'encoder.pkl')

with open(model_path, 'wb') as f:
    pickle.dump(xgb_model, f)

with open(scaler_path, 'wb') as f:
    pickle.dump(scaler, f)

with open(encoder_path, 'wb') as f:
    pickle.dump(coder, f)

print("\n" + "=" * 50)
print("MODEL SAVED SUCCESSFULLY")
print("=" * 50)
print(f"Model saved to: {model_path}")
print(f"Scaler saved to: {scaler_path}")
print(f"Encoder saved to: {encoder_path}")
print(f"Feature columns: {X_test_transformed.columns.tolist()}")