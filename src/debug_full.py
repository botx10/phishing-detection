# debug_full.py
import joblib
import pandas as pd
import sys
from kaggle_features import load_kaggle_columns, extract_kaggle_features

MODEL_PATH = "../models/phish_model_kaggle.pkl"

def show(features, df, model):
    print("\n--- Selected feature values ---")
    interesting = [
        'qty_dot_url','qty_hyphen_url','length_url','qty_dot_domain','domain_length',
        'time_domain_activation','time_domain_expiration','tls_ssl_certificate',
        'qty_ip_resolved','qty_nameservers','qty_mx_servers','url_google_index'
    ]
    for f in interesting:
        if f in features:
            print(f"{f}: {features[f]}")
    print("\n--- Full tail of features (last 30 cols) ---")
    for c in df.columns[-30:]:
        print(c, ":", df.iloc[0][c])
    print("\n--- Model prediction & probs ---")
    pred = int(model.predict(df)[0])
    probs = model.predict_proba(df)[0]
    print("Pred:", pred, "probs:", probs)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_full.py <url>")
        sys.exit(1)
    url = sys.argv[1]
    print("URL:", url)

    cols, label = load_kaggle_columns("../data/raw/kaggle_phish.csv")
    print("Detected columns:", len(cols), "label:", label)

    feats = extract_kaggle_features(url, expected_columns=cols, do_whois=True)
    df = pd.DataFrame([feats], columns=cols)
    df = df.fillna(0)
    df = df.replace(-1, 0)

    model = joblib.load(MODEL_PATH)
    print("\nTotal features in vector:", len(feats))
    show(feats, df, model)
