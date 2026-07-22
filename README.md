# WEOTT Proposal Engine — Production

Production deployment of the West End on the Thames PDF proposal orchestrator.

**Live backend URL:** https://stargtm-kkzz.onrender.com  
**App monorepo:** https://github.com/IanDev-cmd/proposal-builder-  
**This repo:** production-ready engine package (templates, inserts, Flask API).

## Deploy

```bash
pip install -r requirements.txt
gunicorn app:app
# or: python app.py
```

Render service should serve at **https://stargtm-kkzz.onrender.com**.

## Endpoints

- `GET /` — health
- `GET /templates` — proposal template catalog
- `GET /inserts` — optional insert catalog (vessel / staff / map)
- `POST /generate` — JSON payload → PDF (supports `template_id` + `selectedInserts`)

## Env

- `PORT` — listen port (default 8000)

## n8n

`QuoteBuilder` HTTP Request node → `POST https://stargtm-kkzz.onrender.com/generate`
