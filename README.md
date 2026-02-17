# healAssi-back

Backend for the HealAssi project (FastAPI).

Quick start

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Preparing to push to GitHub

- This repo uses a local SQLite file `health.db`. Make sure it is not committed. If it was already committed, remove it from the index before pushing:

```bash
# remove tracked DB file, keep local copy
git rm --cached health.db || true
git commit -m "Remove local DB from repository" || true
```

- Initialize and push (example):

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-git-remote-url>
git push -u origin main
```

Replace `<your-git-remote-url>` with your GitHub repo URL.

Notes

- `.gitignore` already added to ignore `health.db`, virtualenvs and common files.
- If you need CI, license, or PR templates, tell me and I'll add them.
