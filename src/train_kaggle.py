# src/train_kaggle.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

# === Paths ===
DATA_PATH = "../data/raw/kaggle_phish.csv"
MODEL_PATH = "../models/phish_model_kaggle.pkl"

print("📂 Loading dataset...")
df = pd.read_csv(DATA_PATH, encoding="utf-8-sig")

# Automatically detect label column
label_col = None
for c in df.columns:
    if 'label' in c.lower() or 'phish' in c.lower() or 'result' in c.lower() or 'class' in c.lower():
        label_col = c
        break

if label_col is None:
    raise ValueError("❌ Could not find label column in dataset.")

print(f"✅ Detected label column: {label_col}")

# Separate features and labels
X = df.drop(columns=[label_col])
y = df[label_col]

# Handle missing values
X = X.fillna(0)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train RandomForest
print("🧠 Training model on Kaggle dataset...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("\n=== Evaluation Results ===")
print(classification_report(y_test, y_pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
print(f"✅ Accuracy: {accuracy_score(y_test, y_pred):.4f}")

# Save model
joblib.dump(model, MODEL_PATH)
print(f"\n💾 Model saved to {MODEL_PATH}")
