# src/api.py (WHOIS-enabled, CORS, API-key, rate-limited)
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
    # If our repo was copied to /opt/render/project/src and files are under src/, we might have src/src
    # Add both THIS_DIR and its parent to sys.path to be robust.
    PARENT_DIR = os.path.dirname(THIS_DIR)
    if THIS_DIR not in sys.path:
        sys.path.insert(0, THIS_DIR)
    if PARENT_DIR not in sys.path:
        sys.path.insert(0, PARENT_DIR)
    log(f"DEBUG: added to sys.path: {THIS_DIR} and {PARENT_DIR}")
except Exception:
    log("WARN: failed to adjust sys.path for local imports")
    traceback.print_exc()

# ---------------- Flask app ----------------
app = Flask(__name__)

# CORS: allow only the frontend origin (set FRONTEND_ORIGIN env var). For local dev you can set to http://127.0.0.1:8000
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:8000")
CORS(app, resources={r"/*": {"origins": FRONTEND_ORIGIN}},
     supports_credentials=False,
     allow_headers=["Content-Type", "x-api-key", "Authorization", "X-Requested-With"])

# Rate limiter (per-IP). Adjust limits as needed.
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
    try:
        expected_cols, label_col = load_kaggle_columns("../data/raw/kaggle_phish.csv")
        log(f"API: expecting features: {len(expected_cols)} features")
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

MODEL_PATH = "../models/phish_model_kaggle.pkl"
model = None
try:
    log(f"DEBUG: loading model from {MODEL_PATH} ...")
    start = time.time()
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
        data = request.get_json() or {}
        url = data.get('url', '')
        if not url:
            return jsonify({'error': 'No URL provided'}), 400

        # Extract features (do_whois=True for richer features; may be slower)
        feats = extract_kaggle_features(url, expected_columns=expected_cols, do_whois=True)

        # Build DataFrame in expected column order
        if expected_cols:
            df = pd.DataFrame([feats], columns=expected_cols)
        else:
            df = pd.DataFrame([feats])

        # safe numeric defaults
        df = df.fillna(0)
        df = df.replace(-1, 0)

        # Predict
        pred = int(model.predict(df)[0])
        prob = float(model.predict_proba(df).max())
        label = "Phishing" if pred == 1 else "Legitimate"

        # Explain (if available)
        contribs = []
        if explain_instance:
            try:
                contribs = explain_instance(df) or []
            except Exception:
                log("WARN: explain_instance failed")
                traceback.print_exc()

        return jsonify({
            'url': url,
            'prediction': label,
            'confidence': round(prob, 3),
            'top_contributions': contribs[:6]
        })

    except Exception as e:
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
