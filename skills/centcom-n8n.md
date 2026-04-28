# Contro1 n8n Skill

Use this when building n8n workflows with Contro1.

## Rules

- Use an HTTP Request node to create approval requests before risky writes.
- Use an HTTP Request node to create audit records after allowed autonomous actions.
- Use a stable `thread_id` per n8n execution so requests and logs appear in one timeline.
- Use `external_request_id` for idempotency and keep it unique per approval step.
- Use `in_reply_to` when logging a follow-up after a Contro1 request.

## Audit record HTTP body

```json
{
  "action": "n8n.action_completed",
  "summary": "Workflow completed an authorized action",
  "source": {
    "integration": "n8n",
    "workflow_id": "{{$workflow.id}}",
    "run_id": "{{$execution.id}}"
  },
  "outcome": "success",
  "thread_id": "thr_n8n_{{$execution.id}}",
  "in_reply_to": { "type": "request", "id": "{{$json.request_id}}" }
}
```
---
name: centcom-n8n
description: Guide for integrating n8n workflows with CENTCOM via HTTP Request and Wait webhook resume.
user_invocable: true
---

# CENTCOM + n8n Skill

Use this skill when a user wants n8n workflow approvals handled by CENTCOM with production-safe pause/resume behavior.

## Installation (optional bridge proxy)

If you use the callback proxy script at https://github.com/contro1-hq/centcom-n8n/blob/main/examples/n8n_callback_proxy.py:

```bash
pip install centcom flask python-dotenv requests
```

n8n itself requires no installation - it runs as a service.

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
7. For high-risk actions, set `approval_policy` so n8n resumes only after quorum.

## Required CENTCOM request fields

```json
{
  "type": "approval",
  "question": "Approve deployment?",
  "context": "n8n workflow requests production deploy approval.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume",
  "required_role": "manager",
  "approval_policy": {
    "mode": "threshold",
    "required_approvals": 2,
    "required_roles": ["manager", "admin"],
    "separation_of_duties": true,
    "fail_closed_on_timeout": true
  },
  "metadata": {
    "workflow": "deploy-pipeline",
    "execution_id": "{{$execution.id}}"
  }
}
```

## Multi-approval callback behavior

For a two-person policy, the first approval records an audit event and keeps the workflow paused. CENTCOM calls the n8n resume webhook only when quorum is met, a reviewer rejects, or the request times out. Treat missing quorum as fail-closed for deploys, payments, data deletion, and privilege escalation.

Example high-risk payloads:

```json
{
  "type": "approval",
  "question": "Approve bulk customer data deletion?",
  "context": "Delete 12,430 stale CRM records after retention review.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume",
  "approval_policy": {
    "mode": "threshold",
    "required_approvals": 2,
    "required_roles": ["manager", "admin"],
    "separation_of_duties": true,
    "fail_closed_on_timeout": true
  },
  "metadata": {
    "workflow": "data-retention-cleanup",
    "risk": "bulk_delete"
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
- Resuming n8n after the first approval when `approval_policy.required_approvals` is greater than 1.

## Validation steps

1. Trigger workflow and confirm request appears in CENTCOM queue.
2. For single approval, approve once and verify workflow resumes approved branch.
3. For two-person approval, approve once and verify workflow stays paused until quorum.
4. Reject once and verify workflow goes to fallback branch.
5. Repeat run to confirm metadata correlation remains correct.

## Full reference links

- Repo: https://github.com/contro1-hq/centcom-n8n
- Callback proxy example: https://github.com/contro1-hq/centcom-n8n/blob/main/examples/n8n_callback_proxy.py
- Request payload example: https://github.com/contro1-hq/centcom-n8n/blob/main/examples/request_payload.json
- Skill file source: https://github.com/contro1-hq/centcom-n8n/blob/main/skills/centcom-n8n.md
- Protocol docs: https://contro1.com/docs/audit-records-and-threads
