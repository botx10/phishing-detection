# PhishGuard — AI Phishing Detection (Demo)

## Run locally
1. Create venv:
   python -m venv venv
2. Activate:
   .\venv\Scripts\activate
3. Install:
   pip install -r requirements.txt
4. Start API:
   python src\api.py
5. Open frontend:
   cd Frontend
   python -m http.server 8000
   Open http://127.0.0.1:8000

## Notes
- Do NOT store secrets in repo. Use environment variables.
- Model file may be large; use Git LFS or external storage.
