# WEOTT Proposal Engine — Production

Production deployment of the West End on the Thames PDF proposal orchestrator.

**Live backend URL:** https://weott-proposal-engine.onrender.com  
**App monorepo:** https://github.com/IanDev-cmd/proposal-builder-  
**This repo:** production-ready engine package (templates, inserts, Flask API).

## Deploy

```bash
pip install -r requirements.txt
gunicorn app:app
# or: python app.py
```

Render service should serve at **https://weott-proposal-engine.onrender.com**.

## Endpoints

- `GET /` — health
- `GET /templates` — proposal template catalog
- `GET /inserts` — optional insert catalog (vessel / staff / map)
- `POST /generate` — JSON payload → PDF (supports `template_id` + `selectedInserts`)

## Env

- `PORT` — listen port (default 8000)

## Callers

The React workspace SPA posts to `POST /generate` directly (CORS enabled). Do not route PDFs through n8n.

n8n `https://harmonyproxy.app.n8n.cloud` remains only for Gemini:

- `PrefillHealer`
- `LeadNotesSummary`

Google Sheets OAuth on that instance is unused after the Apps Script cutover.
