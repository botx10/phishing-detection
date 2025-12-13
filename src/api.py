# src/api.py (WHOIS-enabled, CORS, API-key, rate-limited) - with SHAP fallback to feature_importances_
import os
import time
import sys
import traceback
import joblib
import pandas as pd

from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

print("DEBUG: starting api.py")

def log(msg):
    print(msg)
    sys.stdout.flush()

# ---------------- Ensure local src directory is on Python path ----------------
# This makes imports like "import kaggle_features" work even if the app is started
# from a nested directory (common on some hosts like Render).
try:
    THIS_FILE = os.path.abspath(__file__)
    THIS_DIR = os.path.dirname(THIS_FILE)        # .../project/src
    REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
    PARENT_DIR = os.path.dirname(THIS_DIR)  # same as REPO_ROOT in typical layout
    # Add both THIS_DIR and REPO_ROOT to sys.path to be robust
    if THIS_DIR not in sys.path:
        sys.path.insert(0, THIS_DIR)
    if REPO_ROOT not in sys.path:
        sys.path.insert(0, REPO_ROOT)
    log(f"DEBUG: added to sys.path: {THIS_DIR} and {REPO_ROOT}")
except Exception:
    log("WARN: failed to adjust sys.path for local imports")
    traceback.print_exc()

# ---------------- Flask app ----------------
app = Flask(__name__)

# CORS: allow only the frontend origin (set FRONTEND_ORIGIN env var).
# For local dev set FRONTEND_ORIGIN to e.g. http://127.0.0.1:8000 or http://localhost:3000
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
CORS(app, resources={r"/*": {"origins": FRONTEND_ORIGIN}},
     supports_credentials=False,
     allow_headers=["Content-Type", "x-api-key", "Authorization", "X-Requested-With"])

# Rate limiter (per-IP). Adjust limits as needed.
# Flask-Limiter v3+ syntax
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60 per minute"]
)
limiter.init_app(app)


# API key from environment (optional but recommended)
API_KEY = os.getenv("API_KEY", None)

def require_api_key():
    """Abort with 401 if API_KEY is set and the request header does not match."""
    if API_KEY:
        key = request.headers.get("x-api-key")
        if not key or key != API_KEY:
            abort(401, description="Unauthorized (missing or invalid API key)")

@app.after_request
def set_secure_headers(response):
    # Basic secure headers
    response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
    response.headers.setdefault('X-Content-Type-Options', 'nosniff')
    response.headers.setdefault('X-Frame-Options', 'DENY')
    return response

# ---------------- Load Kaggle columns & model ----------------
expected_cols = None
label_col = None

# Import feature extractor safely and report clear error if fails
try:
    from kaggle_features import load_kaggle_columns, extract_kaggle_features
    log("DEBUG: imported kaggle_features")
    # attempt to load the CSV from repo root/data/raw/kaggle_phish.csv
    try:
        kaggle_csv_path = os.path.abspath(os.path.join(REPO_ROOT, "data", "raw", "kaggle_phish.csv"))
        if os.path.exists(kaggle_csv_path):
            expected_cols, label_col = load_kaggle_columns(kaggle_csv_path)
            log(f"API: expecting features: {len(expected_cols) if expected_cols else 0} features (loaded from {kaggle_csv_path})")
        else:
            log(f"WARN: kaggle CSV not found at {kaggle_csv_path}; load_kaggle_columns was not called.")
            expected_cols = None
            label_col = None
    except Exception:
        log("WARN: failed to load kaggle CSV columns; continuing with None.")
        traceback.print_exc()
        expected_cols = None
        label_col = None
except Exception:
    log("ERROR: runtime import of kaggle_features failed")
    traceback.print_exc()
    # keep the names defined but set to None so predict() can return a helpful error
    load_kaggle_columns = None
    extract_kaggle_features = None
    expected_cols = None
    label_col = None

# Resolve model path robustly relative to repo root
MODEL_FILENAME = "phish_model_kaggle.pkl"
MODEL_PATH = os.path.abspath(os.path.join(REPO_ROOT, "models", MODEL_FILENAME))
model = None
try:
    log(f"DEBUG: loading model from {MODEL_PATH} ...")
    start = time.time()
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    log(f"DEBUG: model loaded in {time.time()-start:.2f}s")
except Exception:
    log("ERROR loading model:")
    traceback.print_exc()
    model = None

# Optional SHAP explain util
try:
    from shap_utils import explain_instance
    log("DEBUG: shap_utils imported")
except Exception:
    explain_instance = None
    log("DEBUG: shap_utils not available; explanations disabled")

# ---------------- Routes ----------------
@app.route('/')
def home():
    return "Phishing Detection API is running!"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": bool(model),
        "feature_extractor_available": bool(extract_kaggle_features),
        "expected_feature_count": len(expected_cols) if expected_cols else None
    })

@app.route('/predict', methods=['POST'])
@limiter.limit("30 per minute")
def predict():
    # enforce API key if configured
    require_api_key()

    # quick checks
    if extract_kaggle_features is None:
        return jsonify({'error': 'Feature extractor not available on server (kaggle_features import failed)'}), 500
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    try:
        data = request.get_json(force=True) or {}
        url = data.get('url', '') or ''
        do_whois = data.get('do_whois', True)

        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Extract features (do_whois flag can be toggled)
        feats = extract_kaggle_features(url, expected_columns=expected_cols, do_whois=bool(do_whois))

        # Build DataFrame in expected column order (robustly)
        # feats can be dict or list-like depending on your extractor; handle dict case
        if isinstance(feats, dict):
            df = pd.DataFrame([feats])
        else:
            # assume list-like
            df = pd.DataFrame([feats])

        if expected_cols:
            # Reindex to the expected columns, filling missing cols with zeros
            df = df.reindex(columns=expected_cols, fill_value=0)

        # safe numeric defaults
        df = df.fillna(0)
        df = df.replace(-1, 0)

        # Predict - some models may not have predict_proba
        pred_raw = model.predict(df)
        try:
            pred = int(pred_raw[0]) if hasattr(pred_raw, "__iter__") else int(pred_raw)
        except Exception:
            # fallback if predict returns something else
            pred = int(pred_raw)

        prob = None
        try:
            proba_arr = model.predict_proba(df)
            # find probability of predicted class
            if hasattr(proba_arr, "shape"):
                prob = float(proba_arr.max())
            else:
                # unexpected format; fallback
                prob = None
        except Exception:
            # model doesn't support predict_proba or it failed
            log("WARN: predict_proba not available or failed; continuing without confidence")
            prob = None

        label = "Phishing" if pred == 1 else "Legitimate"

        # ---------------- Explain (if available) with fallback ----------------
        contribs = []
        # Try shap-based explanations first (if shap_utils.explain_instance is available)
        if explain_instance:
            try:
                contribs = explain_instance(df) or []
            except Exception:
                log("WARN: explain_instance failed")
                traceback.print_exc()
                contribs = []

        # Fallback: if SHAP not available or returned empty, try model.feature_importances_
        if (not contribs or len(contribs) == 0) and hasattr(model, "feature_importances_"):
            try:
                import numpy as np
                cols = list(df.columns)
                fi = getattr(model, "feature_importances_", None)
                if fi is not None:
                    fi = np.array(fi)
                    # If feature_importances_ length matches columns, pair them
                    if fi.shape[0] == len(cols):
                        pairs = sorted(zip(cols, fi.tolist()), key=lambda x: abs(x[1]), reverse=True)
                    else:
                        # if sizes mismatch, try to use first-n
                        pairs = sorted(zip(cols, fi[:len(cols)].tolist()), key=lambda x: abs(x[1]), reverse=True)
                    contribs = [{"feature": name, "contribution": float(val)} for name, val in pairs[:12]]
                    log("DEBUG: using feature_importances_ fallback for top_contributions")
            except Exception:
                log("WARN: feature_importances_ fallback failed")
                traceback.print_exc()

        # If still empty, contribs will be empty list (frontend will show "No contributions")

        response = {
            'url': url,
            'prediction': label,
            'confidence': round(prob, 3) if prob is not None else None,
            'top_contributions': contribs[:6] if isinstance(contribs, list) else []
        }
        return jsonify(response), 200

    except Exception as e:
        log("ERROR in /predict:")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ---------------- Run app ----------------
if __name__ == '__main__':
    log("DEBUG: entering app.run()")
    try:
        port = int(os.getenv("PORT", "5000"))
        # host 0.0.0.0 so Render / Gunicorn can bind correctly
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception:
        log("ERROR running Flask:")
        traceback.print_exc()

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = FRONTEND_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, x-api-key"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response
