#!/bin/bash
# Start Brand Alnashme locally:  ./run.sh
cd "$(dirname "$0")"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
echo "Store:  http://localhost:8000"
echo "Admin:  http://localhost:8000/admin   (admin / admin)"
uvicorn app.main:app --reload --port 8000
