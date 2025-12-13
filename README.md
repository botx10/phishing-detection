# PhishGuard — Phishing Detection & Prevention Dashboard

PhishGuard is a machine learning–based phishing URL detection system with an interactive, SOC-style dashboard.  
It helps users identify potentially malicious URLs and understand *why* a link may be risky through explainable indicators.

The system focuses on **early detection and user awareness**, contributing to phishing prevention by warning users before they interact with suspicious links.

---

## 🚀 Features

- 🔍 **Real-time phishing detection** using a trained ML model  
- 📊 **Confidence scoring** for each prediction  
- 🧠 **Explainable risk indicators (XAI)** with human-readable explanations  
- 🟢 / 🔴 **Clear verdicts** for legitimate vs phishing URLs  
- 📜 **Session-based scan history**  
- 🖥️ **SOC-style dark dashboard UI**

---

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Framer Motion

### Backend
- Python
- Flask
- REST API
- CORS & rate limiting

### Machine Learning
- Random Forest classifier
- Feature-based phishing detection
- Trained on Kaggle phishing dataset
- Global feature importance with explainable indicators

---

## 🧠 How It Works (High-Level)

1. User submits a URL
2. Backend extracts structural and domain-based features
3. ML model predicts **Phishing** or **Legitimate**
4. Confidence score is generated
5. Top contributing indicators are shown with explanations
6. User is warned before visiting the link

---

## 🧪 Example Use Cases

- Testing suspicious links before opening them
- Cybersecurity education & awareness
- Academic demonstrations of phishing detection
- SOC-style monitoring dashboards

---


