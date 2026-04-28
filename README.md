# centcom-n8n

n8n starter kit for Contro1/CENTCOM pause-resume workflows.

## Protocol

This starter uses **Contro1 Integration Protocol v1**:

- canonical request object (`Contro1Request`)
- canonical response object (`Contro1Response`)
- continuation mode: `decision` for wait/resume flow
- routing metadata in request payload

## Files

- `docs/n8n-connector.md`
- `skills/centcom-n8n.md`
- `.env.example`
- `requirements.txt`
- `examples/n8n_callback_proxy.py`
- `examples/request_payload.json`

## Quick Start

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python examples/n8n_callback_proxy.py
```

Proxy runs on `http://localhost:8083`.

## Smoke Test

1. Configure n8n `Wait (On Webhook Call)` URL in `.env` as `N8N_RESUME_URL`.
2. Create a request in CENTCOM with callback URL: `http://localhost:8083/centcom-callback`.
3. Approve/deny in CENTCOM.
4. Verify proxy logs callback and forwards payload to n8n resume URL.

## Security defaults

- Do not hardcode API keys in workflow JSON.
- Use env-backed header in n8n:
  - `Authorization: Bearer {{$env.CENTCOM_API_KEY}}`
- Verify callback signatures in proxy/bridge services.
- Protect n8n resume webhook URLs (auth/token where possible).

## Request vs audit log

Use `POST /api/centcom/v1/requests` when the workflow must pause for a human. Use `POST /api/centcom/v1/audit-records` when the workflow performed an allowed action and only needs a durable record.

## Thread pattern

Derive one `thread_id` per n8n execution:

```json
{
  "thread_id": "thr_n8n_{{$execution.id}}",
  "external_request_id": "n8n:{{$workflow.id}}:{{$execution.id}}:approval"
}
```

When the Wait node resumes and a follow-up action runs, log it in the same thread:

```json
{
  "action": "n8n.crm_sync_completed",
  "summary": "Synced approved CRM records to production",
  "source": { "integration": "n8n", "workflow_id": "{{$workflow.id}}", "run_id": "{{$execution.id}}" },
  "outcome": "success",
  "thread_id": "thr_n8n_{{$execution.id}}",
  "in_reply_to": { "type": "request", "id": "{{$json.request_id}}" }
}
```
