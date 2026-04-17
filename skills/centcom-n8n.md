---
name: centcom-n8n
description: Guide for integrating n8n workflows with CENTCOM via HTTP Request and Wait webhook resume.
user_invocable: true
---

# CENTCOM + n8n Skill

Use this skill when a user wants n8n workflow approvals handled by CENTCOM with production-safe pause/resume behavior.

## Installation (optional bridge proxy)

If you use the callback proxy script (`examples/n8n_callback_proxy.py`):

```bash
pip install centcom flask python-dotenv requests
```

n8n itself requires no installation — it runs as a service.

## Required configuration

n8n environment variables (set in n8n settings or `.env`):

```bash
CENTCOM_API_KEY=your_centcom_api_key
CENTCOM_BASE_URL=https://api.contro1.com/api/centcom/v1
CENTCOM_WEBHOOK_SECRET=whsec_your_signing_secret
```

Use in HTTP Request node headers:
- `Authorization: Bearer {{$env.CENTCOM_API_KEY}}`
- POST URL: `{{$env.CENTCOM_BASE_URL}}/requests`

## What to build

Build an n8n workflow that:

1. Creates a CENTCOM request via HTTP.
2. Pauses until a callback is received.
3. Branches on approval result.
4. Continues execution only on approved path.

## Implementation steps (recommended)

1. Create request with n8n HTTP Request node.
2. Set `callback_url` to a workflow endpoint that feeds the resume path.
3. Pause with Wait node (`On Webhook Call`) and enable authentication.
4. Resume via callback and branch by approval result (`approved` or boolean `value`).
5. Keep execution metadata in request `metadata` (workflow ID, execution ID, entity ID).
6. Add timeout and fallback branch for expired/denied cases.

## Required CENTCOM request fields

```json
{
  "type": "approval",
  "question": "Approve deployment?",
  "context": "n8n workflow requests production deploy approval.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume",
  "required_role": "manager",
  "metadata": {
    "workflow": "deploy-pipeline",
    "execution_id": "{{$execution.id}}"
  }
}
```

## Node-level checklist

- HTTP Request node
  - Method: `POST`
  - URL: `{{$env.CENTCOM_BASE_URL}}/requests`
  - Auth header: `Authorization: Bearer {{$env.CENTCOM_API_KEY}}`
- Wait node
  - Resume mode: `On Webhook Call`
  - Auth: enable Header/JWT/Basic where possible
- IF/Switch node
  - Approved path -> continue action
  - Rejected/timeout path -> safe stop and notify

## Common mistakes to avoid

- Using no auth on resume webhook in production.
- Not validating CENTCOM callback signatures when using a proxy/bridge endpoint.
- Not storing execution correlation in `metadata`.
- Treating all responses as `approved`; always parse and validate.
- Missing idempotency in retried create requests.

## Validation steps

1. Trigger workflow and confirm request appears in CENTCOM queue.
2. Approve once and verify workflow resumes approved branch.
3. Reject once and verify workflow goes to fallback branch.
4. Repeat run to confirm metadata correlation remains correct.
