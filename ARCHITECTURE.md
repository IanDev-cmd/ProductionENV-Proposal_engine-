# Proposal engine architecture

Flask service that builds WEOTT proposal PDFs and stores shared workspace quotes.

```mermaid
flowchart LR
  SPA[Workspace SPA] -->|POST /generate| PDF[engine.build_proposal]
  SPA -->|PUT /workspace/quotes/:id| Store[workspace_store.put_quote]
  PDF --> Templates[assets/templates + inserts]
  Store --> JSON[(data/workspace/quotes/*.json)]
  JSON --> Status[reviewStatus pending / approved / disapproved]
```

Workspace quote JSON includes costing snapshot plus `reviewStatus` and `reviewedAt`. A save that omits `reviewStatus` keeps the previous approval so costing edits do not wipe a review.
