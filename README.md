# centcom-n8n

n8n starter kit for Contro1/CENTCOM pause-resume workflows.

This starter uses **Contro1 Integration Protocol v1**:

- canonical request object (`Contro1Request`) and response (`Contro1Response`)
- continuation mode: `decision` for wait/resume flow
- routing metadata in request payload
- case correlation via `correlation_id`

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

## Request example

Send this body from an n8n HTTP Request node. Set `correlation_id` to `{{$execution.id}}` to group all events from the same workflow run into one case timeline.

```json
{
  "type": "approval",
  "question": "Approve deployment?",
  "context": "n8n workflow requests production deploy approval.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume",
  "correlation_id": "{{$execution.id}}",
  "required_role": "manager",
  "approval_policy": {
    "mode": "threshold",
    "required_approvals": 2,
    "required_roles": ["manager", "admin"],
    "separation_of_duties": true,
    "fail_closed_on_timeout": true
  },
  "metadata": {
    "workflow": "deploy-pipeline"
  }
}
```

## Control Map preview

For workflows with `required_roles` or two-person approval, add an HTTP Request node before the approval step to confirm routing is ready.

```
POST {{$env.CENTCOM_BASE_URL}}/requests/control-map
Authorization: Bearer {{$env.CENTCOM_API_KEY}}

{
  "approval_requirements": { "required_roles": ["manager"], "required_approvals": 2 },
  "approval_policy": {
    "mode": "threshold",
    "required_approvals": 2,
    "separation_of_duties": true,
    "fail_closed_on_timeout": true
  }
}
```

If `satisfiable` is `false`, route to an error branch before the Wait node.

## Security defaults

- Do not hardcode API keys in workflow JSON.
- Use env-backed header in n8n:
  - `Authorization: Bearer {{$env.CENTCOM_API_KEY}}`
- Verify callback signatures in proxy/bridge services.
- Protect n8n resume webhook URLs (auth/token where possible).

## Governance readiness

For teams operating AI in regulated environments:
- [EU AI Act readiness guide](https://contro1.com/guides/eu-ai-act-readiness)
- [US AI Governance readiness guide](https://contro1.com/guides/us-ai-governance-readiness)
