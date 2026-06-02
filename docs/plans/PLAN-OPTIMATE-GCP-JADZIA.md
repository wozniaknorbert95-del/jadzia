# PLAN-OPTIMATE-GCP — Jadzia Core

Status: ACCEPTED · Scope: Add Gemini client for descriptive research; keep operational flows deterministic.

## Minimal changes
1) `interfaces/gemini_client.py` — lazy SDK import, `generate(prompt, ...)` method; key from `GOOGLE_API_KEY` (OS env).
2) New endpoint `/ai/research` (FastAPI) — calls client; HITL only; logs stored locally.
3) No change to deploy/SSH pipelines; no AI in critical ops.

## Env
- PowerShell: `[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "paste-key-here", "User")`
- Do not commit `.env`.

## Tests
- Unit: mock client returns; 200 OK with non-empty text.
- Narrow timeout; handle NotConfigured.
