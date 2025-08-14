🛡️ Vulnerability Scanner Dashboard

A web-based dashboard for real-time visualization, and management of system vulnerabilities using integrations with leading scanners like Nessus.


Edit .env and set:

NESSUS_BASE=https://localhost:8834

NESSUS_ACCESS=YOUR_ACCESS_KEY

NESSUS_SECRET=YOUR_SECRET_KEY

NESSUS_VERIFY_TLS=false

🛠️ Local Development

Run backend:

cd backend

python -m venv venv

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload --port 8000

Test:

Swagger Docs → http://localhost:8000/docs

List scans → http://localhost:8000/scans

Run frontend:

cd frontend

npm install

npm run dev

Open the dashboard: http://localhost:5173
