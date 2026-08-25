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

Live instance: `https://harmony9.app.n8n.cloud` (`0b033e4dea3e06f7022fa976138770d89a94a569a45a7883de93bf9335d36920`)  
`QuoteBuilder` HTTP Request node → `POST https://weott-proposal-engine.onrender.com/generate`

Credentials bound on that n8n instance:

- `googlePalmApi` `dlay23hFXEWTtpXH` — Google Gemini(PaLM) Api account
- `googleSheetsOAuth2Api` `GZhF0w9mcVHkFaHo` — Google Sheets account
