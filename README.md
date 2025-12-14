# 🔐 PhishGuard — Phishing Detection & Prevention System

PhishGuard is an AI-powered phishing detection system that analyzes URLs in real time to identify malicious phishing attempts.  
It combines machine learning with explainable AI techniques to help users understand *why* a URL is flagged as phishing or legitimate.

---

## 🚀 Live Demo

- **Frontend (Dashboard):** https://phishguard-frontend-subd.onrender.com  
- **Backend API:** https://phishing-detection-k2kh.onrender.com

---

## 🧠 What Does PhishGuard Do?

PhishGuard performs **phishing detection and prevention**:

- **Detection:**  
  Identifies whether a URL is *Phishing* or *Legitimate* using a trained ML model.

- **Prevention:**  
  By warning users *before* they visit a malicious site and explaining the risk factors, PhishGuard helps prevent credential theft and fraud.

---

## ⚙️ System Architecture

User
│
│ (URL)
▼
React Dashboard (Frontend)
│
│ POST /predict
▼
Flask API (Backend)
│
│ Feature Extraction (111 features)
│ ML Model (Random Forest)
│ SHAP Explainability
▼
Prediction + Confidence + Top Risk Indicators


---

## ✨ Key Features

- 🔍 **Real-Time URL Scanning**
- 🤖 **Machine Learning–based Detection**
- 📊 **Explainable AI (Top Risk Indicators)**
- 🧠 **SHAP-based Feature Contributions**
- 🛡️ **Phishing Prevention via Early Warning**
- 🧾 **Scan History (Session-based)**
- 🌙 **SOC-style Dark Dashboard UI**

---

## 📊 Explainable AI (Why This URL Looks Risky)

Instead of acting as a black box, PhishGuard shows:
- Top contributing features influencing the prediction
- Percentage contribution of each feature
- Plain-English explanations for each indicator

This makes the system understandable for **both technical and non-technical users**.

---

## 🧪 Example Test URLs

### Phishing (Safe to Test)
http://paypal.com.security-checkupdate.com/login


### Legitimate
https://www.google.com/
https://www.wikipedia.org
https://www.github.com/

---

## 🧰 Tech Stack

### Frontend
- React + Vite
- Tailwind CSS
- Framer Motion

### Backend
- Python
- Flask
- Scikit-learn
- SHAP
- WHOIS & SSL feature extraction

### Deployment
- Render (Frontend & Backend)

---

## 📁 Project Structure

phishing-detection/
│
├── api.py # Flask API
├── feature_extractor.py # URL feature extraction
├── model/ # Trained ML model
├── frontend/ # React dashboard
└── README.md

---

## ⚠️ Limitations

- Confidence scores depend on training data distribution
- Some features may contribute even when their value is zero
- Scan history is stored locally per session (not persistent)

---

## 🔮 Future Enhancements

- Browser extension for real-time prevention
- User-friendly feature explanations for all indicators
- Model retraining with newer phishing datasets
- Persistent scan history & user accounts

---

## 👨‍💻 Author

**Aryaman Menon**  
Cybersecurity & AI Enthusiast  

---

## 📜 Disclaimer

This tool is for educational and research purposes only.  
Do not rely solely on automated predictions for critical security decisions.
