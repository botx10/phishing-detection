# src/shap_utils.py
"""
Explain instance(df) -> list of {feature, contribution}.
Tries SHAP first; if unavailable or fails, falls back to model.feature_importances_ * normalized feature values.
"""

import joblib
import numpy as np

MODEL_PATH = "../models/phish_model_kaggle.pkl"

# detect shap availability
try:
    import shap
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

_model = None
def _load_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model

def explain_instance(df, top_k=6):
    """
    df: pandas.DataFrame with a single row
    returns: list of {"feature": name, "contribution": float} sorted by absolute contribution desc.
    """
    try:
        model = _load_model()
    except Exception:
        return []

    # Try SHAP first (best)
    if SHAP_AVAILABLE:
        try:
            explainer = shap.TreeExplainer(model)
            shap_vals = explainer.shap_values(df)
            # if binary classifier, pick class 1 contributions
            if isinstance(shap_vals, list) and len(shap_vals) >= 2:
                vals = shap_vals[1][0]
            else:
                # regression or other -> take first row
                vals = shap_vals[0] if isinstance(shap_vals, (list, tuple)) else shap_vals[0]
            features = df.columns.tolist()
            contribs = [{"feature": f, "contribution": float(v)} for f, v in zip(features, vals)]
            contribs_sorted = sorted(contribs, key=lambda x: abs(x["contribution"]), reverse=True)[:top_k]
            return contribs_sorted
        except Exception:
            # fall through to fallback
            pass

    # Fallback: feature_importances_ * normalized feature value
    try:
        if hasattr(model, "feature_importances_"):
            fi = np.array(getattr(model, "feature_importances_"))
        elif hasattr(model, "coef_"):
            fi = np.abs(np.array(getattr(model, "coef_")).ravel())
        else:
            fi = None

        features = df.columns.tolist()
        vals = df.iloc[0].astype(float).values
        if fi is not None and len(fi) == len(vals):
            norm_vals = vals / (1.0 + np.abs(vals))
            raw = fi * norm_vals
            contribs = [{"feature": f, "contribution": float(r)} for f, r in zip(features, raw)]
            contribs_sorted = sorted(contribs, key=lambda x: abs(x["contribution"]), reverse=True)[:top_k]
            return contribs_sorted
    except Exception:
        pass

    return []
