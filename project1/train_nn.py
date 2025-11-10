# placeholder, replace with the real content after unzip if needed
# train_nn.py — Enhanced retraining script for feedback-based ML model
import pandas as pd
import joblib, json, os
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix

ARTDIR = Path("artifacts")
ARTDIR.mkdir(exist_ok=True)

def load_feedback_data():
    """
    Load feedback from CSV or JSON (whichever exists).
    Returns a cleaned pandas DataFrame.
    """
    csv_path = Path("feedback_log.csv")
    json_path = Path("feedback_log.json")

    if csv_path.exists():
        print("📂 Loading data from feedback_log.csv ...")
        df = pd.read_csv(csv_path, names=["timestamp", "url", "score", "stars", "feedback"])
    elif json_path.exists():
        print("📂 Loading data from feedback_log.json ...")
        with open(json_path) as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    else:
        raise FileNotFoundError("❌ No feedback_log.csv or feedback_log.json found.")

    # Clean and preprocess
    df = df.dropna(subset=["score", "feedback"])
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])
    df["label"] = df["feedback"].apply(lambda x: 1 if "Credible" in str(x) else 0)
    df = df.drop_duplicates(subset=["url", "feedback"], keep="last")
    print(f"✅ Loaded {len(df)} records after cleaning.")
    return df

def train_model(df: pd.DataFrame):
    """Train a simple logistic regression model."""
    X = df[["score"]]  # Using only credibility score as numeric feature
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Evaluate
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    cm = confusion_matrix(y_test, preds)

    # Save model
    joblib.dump(model, ARTDIR / "model.joblib")
    print(f"\n🎯 Model retrained successfully.")
    print(f"📊 Accuracy: {acc:.3f}")
    print("📈 Confusion Matrix:")
    print(cm)
    print(f"💾 Model saved to: {ARTDIR / 'model.joblib'}")

def main():
    try:
        df = load_feedback_data()
        print(f"Class balance:\n{df['label'].value_counts()}\n")
        train_model(df)
    except Exception as e:
        print(f"❌ Training failed: {e}")

if __name__ == "__main__":
    main()
