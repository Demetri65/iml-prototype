# Local Setup (Beginner Friendly)

This project runs two parts at the same time:
- Frontend: a Next.js web app
- Backend: a FastAPI server with a simple /api/health endpoint

Follow the steps in order. Copy and paste the commands exactly as shown.

## 1) Install the tools (one time)

You need:
- Git (downloads the project)
- Node.js 18+ (runs the web app)
- pnpm (installs Node packages)
- Python 3.10+ (runs the API server)

Mac
1. Open Terminal and run `git --version`. If macOS asks to install Command Line Tools, click Install.
2. Install Node.js (LTS): https://nodejs.org
3. Install pnpm: `npm install -g pnpm`
4. Install Python 3: https://www.python.org/downloads/

Windows
1. Install Git: https://git-scm.com/downloads
2. Install Node.js (LTS): https://nodejs.org
3. Install pnpm: open PowerShell and run `npm install -g pnpm`
4. Install Python 3: https://www.python.org/downloads/ (check "Add python to PATH")

Close and reopen your terminal, then check:

```bash
git --version
node --version
pnpm --version
python --version
```

If `python --version` fails on Mac, try `python3 --version`. If only `python3` works, replace `python` with `python3` in the commands below.

## 2) Download the project (git clone)

```bash
git clone <PASTE_THE_REPO_URL_HERE>
cd iml-prototype
```

## 3) Install dependencies

Node packages:

```bash
pnpm install
```

Python packages:

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Mac/Linux:

```bash
source .venv/bin/activate
```

Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then install Python packages:

```bash
pip install -r requirements.txt
```

## 4) Run the app

Keep the virtual environment active, then run:

```bash
pnpm dev
```

Leave this terminal open. When you see logs from both Next.js and Uvicorn, open:
- http://localhost:3000
- http://localhost:3000/api/health
- http://localhost:8000/docs

To stop the app, press Ctrl+C in the terminal.

## Troubleshooting

- "pnpm: command not found": install pnpm and reopen your terminal.
- "python: command not found": reinstall Python and make sure it is on PATH.
- Port 3000 or 8000 already in use: close the other app or restart your computer.
