# src/api.py (WHOIS-enabled, CORS, API-key, rate-limited) - robust import + runtime guard
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

# ---------------- Flask app ----------------
app = Flask(__name__)

# FRONTEND_ORIGIN: comma-separated list allowed, or default localhost for dev
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://127.0.0.1:8000")
if FRONTEND_ORIGIN.strip() == "*":
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False,
         allow_headers=["Content-Type", "x-api-key", "Authorization", "X-Requested-With"])
else:
    allowed = [o.strip() for o in FRONTEND_ORIGIN.split(",") if o.strip()]
    CORS(app, resources={r"/*": {"origins": allowed}}, supports_credentials=False,
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

# ---------------- Load Kaggle columns & attempt import of feature extractor ----------------
expected_cols = None
label_col = None
extract_kaggle_features = None
try:
    # try to import the module and load columns using an absolute path (robust on Render)
    from kaggle_features import load_kaggle_columns, extract_kaggle_features as _extract_kf
    extract_kaggle_features = _extract_kf
    log("DEBUG: imported kaggle_features (initial)")
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    kaggle_csv = os.path.join(BASE_DIR, "data", "raw", "kaggle_phish.csv")
    log(f"DEBUG: checking Kaggle CSV at: {kaggle_csv} (exists? {os.path.exists(kaggle_csv)})")
    expected_cols, label_col = load_kaggle_columns(kaggle_csv)
    log(f"API: expecting features: {len(expected_cols)} features")
except Exception:
    # don't crash here; we'll try again at runtime if needed
    log("WARN: initial import/load of kaggle_features failed (will retry at request-time)")
    traceback.print_exc()
    extract_kaggle_features = None
    expected_cols = None
    label_col = None

# ---------------- Load model (robust path resolution + debug) ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root (one level above src/)
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(BASE_DIR, "models", "phish_model_kaggle.pkl"))

model = None
try:
    log(f"DEBUG: resolved MODEL_PATH = {MODEL_PATH}")
    log(f"DEBUG: current working dir = {os.getcwd()}")
    log(f"DEBUG: model file exists? {os.path.exists(MODEL_PATH)}")
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

# Allow GET for convenience (returns info) and POST for actual prediction
@app.route('/predict', methods=['GET', 'POST'])
@limiter.limit("30 per minute")
def predict():
    if request.method == 'GET':
        return jsonify({
            "info": "Send a POST request with JSON: {\"url\":\"https://example.com\"} to this endpoint.",
            "note": "POSTs require 'Content-Type: application/json'. If API_KEY is configured, include header 'x-api-key'."
        }), 200

    # POST handling below
    # enforce API key if configured
    require_api_key()

    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    # Ensure feature extractor is available: try importing at runtime if initial import failed
    global extract_kaggle_features, expected_cols
    if extract_kaggle_features is None:
        try:
            log("DEBUG: runtime attempt to import kaggle_features.extract_kaggle_features")
            from kaggle_features import extract_kaggle_features as _extract_kf, load_kaggle_columns as _load_cols
            extract_kaggle_features = _extract_kf
            # attempt to reload expected_cols if missing
            if expected_cols is None:
                BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                kaggle_csv = os.path.join(BASE_DIR, "data", "raw", "kaggle_phish.csv")
                if os.path.exists(kaggle_csv):
                    expected_cols, label_col = _load_cols(kaggle_csv)
                    log(f"DEBUG: runtime loaded expected_cols length: {len(expected_cols)}")
        except Exception:
            log("ERROR: runtime import of kaggle_features failed")
            traceback.print_exc()
            # Informative error for caller (do not call None)
            return jsonify({'error': 'Feature extractor not available on server (kaggle_features import failed)'}), 500

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
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception:
        log("ERROR running Flask:")
        traceback.print_exc()
