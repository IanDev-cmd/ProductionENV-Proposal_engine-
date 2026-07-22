# WEOTT Proposal Engine — Production

Production deployment of the West End on the Thames PDF proposal orchestrator.

**Source of truth (app monorepo):** https://github.com/IanDev-cmd/proposal-builder-  
**This repo:** production-ready engine package (templates, inserts, Flask API).

## Deploy

```bash
pip install -r requirements.txt
gunicorn app:app
# or: python app.py
```

## Endpoints

- `GET /` — health
- `GET /templates` — proposal template catalog
- `GET /inserts` — optional insert catalog (vessel / staff / map)
- `POST /generate` — JSON payload → PDF (supports `template_id` + `selectedInserts`)

## Env

- `PORT` — listen port (default 8000)

Wired from n8n `QuoteBuilder` → `POST /generate`.
