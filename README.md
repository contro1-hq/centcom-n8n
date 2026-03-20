# centcom-n8n

Official CENTCOM connector guides and templates for n8n workflows.

## What this repo provides

- A practical pattern for n8n pause/resume approval flows using built-in nodes.
- Field-level examples for `POST /requests` payloads and callback handling.
- A skill file for AI-assisted implementation and validation.

## Security defaults (required)

- Do not hardcode API keys in workflow JSON.
- Use environment-backed auth headers:

```text
Authorization: Bearer {{$env.CENTCOM_API_KEY}}
```

- If callbacks pass through a proxy/bridge service, verify CENTCOM signatures with:

```bash
CENTCOM_WEBHOOK_SECRET=whsec_your_signing_secret
```

## Recommended architecture

1. Trigger -> Set node prepares context.
2. HTTP Request node creates CENTCOM request.
3. Wait node (`On Webhook Call`) pauses execution.
4. IF/Switch branches on approve vs deny/timeout.

## Quick Start request body

```json
{
  "type": "approval",
  "question": "Approve CRM write-back?",
  "context": "Sync 240 records from staging to production.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume",
  "required_role": "manager",
  "metadata": {
    "workflow": "crm-sync",
    "execution_id": "{{$execution.id}}"
  }
}
```

## Node-level checklist

- HTTP Request:
  - Method `POST`, URL `https://api.contro1.com/api/centcom/v1/requests`
  - Auth header from `{{$env.CENTCOM_API_KEY}}`
- Wait:
  - Resume mode `On Webhook Call`
  - Enable auth where possible
- IF/Switch:
  - `approved == true` -> continue
  - else -> safe fallback

## Production checklist

- Add idempotency key for retried create-request executions.
- Protect resume endpoints from unauthorized calls.
- Validate callback payload before branching.
- Keep correlation IDs in metadata for observability.
- Add explicit timeout handling branch.

## Troubleshooting

- Workflow does not resume: validate `callback_url` reachability and run context.
- Wrong branch decision: verify response parsing (`approved` or boolean `value`).
- Duplicate pending approvals: add deterministic idempotency keys.

## Documentation in this repo

- Guide: `docs/n8n-connector.md`
- Skill: `skills/centcom-n8n.md`

## Related repositories

- [`centcom`](https://github.com/contro1-hq/centcom)
- [`centcom-sdk`](https://github.com/contro1-hq/centcom-sdk)
