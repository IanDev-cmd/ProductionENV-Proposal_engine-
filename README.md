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

## n8n

Live instance: `https://prometheus5.app.n8n.cloud`  
`QuoteBuilder` HTTP Request node → `POST https://weott-proposal-engine.onrender.com/generate`

Credentials bound on that n8n instance:

- `googlePalmApi` `zvFDkn9Cp7SqbA1q` — Google Gemini(PaLM) Api account
- `googleSheetsOAuth2Api` `9DvsM5k7IUgWQ5Bf` — Google Sheets account
