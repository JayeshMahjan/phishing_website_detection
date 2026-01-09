"""
Phishing Website Detection - ML Model Training
================================================
This script trains a Random Forest Classifier to detect phishing websites.

Why Random Forest?
- Handles non-linear relationships well (URLs have complex patterns)
- Resistant to overfitting with proper tuning
- Works well with mixed feature types
- Provides feature importance insights
- Fast prediction time (crucial for web apps)
- No feature scaling required
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
import os

# ===============================================
# 1. LOAD AND EXPLORE DATASET
# ===============================================
print("=" * 60)
print("PHISHING WEBSITE DETECTION - MODEL TRAINING")
print("=" * 60)

# Load dataset (update this path to your CSV file location)
print("\n[1/6] Loading dataset...")
df = pd.read_csv('phishing_dataset.csv')

print(f"✓ Dataset loaded successfully!")
print(f"  Total rows: {len(df):,}")
print(f"  Total columns: {len(df.columns)}")
print(f"\n  Columns: {list(df.columns)}")

# ===============================================
# 2. DATA CLEANING & PREPROCESSING
# ===============================================
print("\n[2/6] Cleaning and preprocessing data...")

# Drop unsafe columns that cause data leakage
columns_to_drop = ['domain', 'ranking', 'valid', 'activeDuration']
existing_cols_to_drop = [col for col in columns_to_drop if col in df.columns]

if existing_cols_to_drop:
    df = df.drop(columns=existing_cols_to_drop)
    print(f"✓ Dropped columns: {existing_cols_to_drop}")

# Check for missing values
missing_values = df.isnull().sum()
if missing_values.sum() > 0:
    print(f"\n⚠ Missing values detected:")
    print(missing_values[missing_values > 0])
    # Fill or drop missing values
    df = df.dropna()
    print(f"✓ Missing values handled. Remaining rows: {len(df):,}")
else:
    print("✓ No missing values found")

# Display class distribution
print("\n  Class Distribution:")
print(df['label'].value_counts())
print(f"  Legitimate: {(df['label'] == 0).sum():,} ({(df['label'] == 0).sum() / len(df) * 100:.1f}%)")
print(f"  Phishing:   {(df['label'] == 1).sum():,} ({(df['label'] == 1).sum() / len(df) * 100:.1f}%)")

# ===============================================
# 3. FEATURE ENGINEERING & SPLITTING
# ===============================================
print("\n[3/6] Splitting dataset into train/test sets...")

# Separate features (X) and target (y)
X = df.drop('label', axis=1)
y = df['label']

print(f"  Features used: {list(X.columns)}")

# Split data: 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2, 
    random_state=42, 
    stratify=y  # Maintain class distribution
)

print(f"✓ Training set: {len(X_train):,} samples")
print(f"✓ Testing set:  {len(X_test):,} samples")

# ===============================================
# 4. MODEL TRAINING
# ===============================================
print("\n[4/6] Training Random Forest Classifier...")

# Initialize Random Forest with optimized parameters
model = RandomForestClassifier(
    n_estimators=100,      # Number of trees
    max_depth=20,          # Maximum depth of trees
    min_samples_split=10,  # Minimum samples to split a node
    min_samples_leaf=4,    # Minimum samples at leaf node
    random_state=42,
    n_jobs=-1,             # Use all CPU cores
    verbose=1
)

# Train the model
model.fit(X_train, y_train)

print("✓ Model training completed!")

# ===============================================
# 5. MODEL EVALUATION
# ===============================================
print("\n[5/6] Evaluating model performance...")

# Make predictions
y_pred = model.predict(X_test)

# Calculate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n{'=' * 60}")
print(f"MODEL ACCURACY: {accuracy * 100:.2f}%")
print(f"{'=' * 60}")

# Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print("                 Predicted")
print("                 Legit  Phishing")
print(f"Actual Legit     {cm[0][0]:>5}  {cm[0][1]:>8}")
print(f"       Phishing  {cm[1][0]:>5}  {cm[1][1]:>8}")

# Classification Report
print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Legitimate', 'Phishing']))

# Feature Importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print("\nFeature Importance:")
for idx, row in feature_importance.iterrows():
    print(f"  {row['feature']:20s}: {row['importance']:.4f}")

# ===============================================
# 6. SAVE MODEL
# ===============================================
print("\n[6/6] Saving trained model...")

# Create model directory if it doesn't exist
os.makedirs('model', exist_ok=True)

# Save model using joblib
model_path = 'model/phishing_model.pkl'
joblib.dump(model, model_path)

print(f"✓ Model saved successfully to: {model_path}")
print(f"\n{'=' * 60}")
print("TRAINING COMPLETED SUCCESSFULLY!")
print(f"{'=' * 60}")
print("\nNext Steps:")
print("1. Run 'python app.py' to start the Flask web application")
print("2. Open your browser and test the phishing detector")
