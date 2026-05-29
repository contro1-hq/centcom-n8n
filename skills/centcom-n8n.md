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
5. Include `correlation_id` in the request body to group related workflow events into one case timeline.
6. Keep additional execution metadata in `metadata` (workflow ID, entity ID).
7. Add timeout and fallback branch for expired/denied cases.
8. For high-risk actions, set `approval_policy` so n8n resumes only after quorum.

## Required CENTCOM request fields

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
    "workflow": "deploy-pipeline",
    "execution_id": "{{$execution.id}}"
  }
}
```

Use `correlation_id` to link this request to audit log entries or follow-up requests in the same workflow run. Any `log_action` call with the same `correlation_id` will appear together in the case timeline.

## Check routing before submitting (Control Map)

For workflows that use `required_roles` or two-person approval, add an HTTP Request node before the approval step to confirm routing is ready. Cache or skip this step for low-risk actions.

```json
POST {{$env.CENTCOM_BASE_URL}}/requests/control-map

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

If the response `satisfiable` field is `false`, route to an error branch and surface `warnings` to the workflow owner before proceeding.

## Multi-approval callback behavior

For a two-person policy, the first approval records an audit event and keeps the workflow paused. CENTCOM calls the n8n resume webhook only when quorum is met, a reviewer rejects, or the request times out. Treat missing quorum as fail-closed for deploys, payments, data deletion, and privilege escalation.

Example high-risk payload:

```json
{
  "type": "approval",
  "question": "Approve bulk customer data deletion?",
  "context": "Delete 12,430 stale CRM records after retention review.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume",
  "correlation_id": "{{$execution.id}}",
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
- Not setting `correlation_id` - without it, audit log entries appear disconnected from the approval request.
- Treating all responses as `approved`; always parse and validate.
- Missing idempotency in retried create requests.
- Resuming n8n after the first approval when `approval_policy.required_approvals` is greater than 1.

## Validation steps

1. Trigger workflow and confirm request appears in CENTCOM queue.
2. For single approval, approve once and verify workflow resumes approved branch.
3. For two-person approval, approve once and verify workflow stays paused until quorum.
4. Reject once and verify workflow goes to fallback branch.
5. Repeat run to confirm `correlation_id` links all events in the same case timeline.

## Governance readiness

For teams operating under EU or US AI governance requirements, see:
- https://contro1.com/guides/eu-ai-act-readiness
- https://contro1.com/guides/us-ai-governance-readiness

## Related integrations

- Python SDK skill: https://github.com/contro1-hq/centcom/blob/main/skills/centcom-python-sdk.md
- JS SDK skill: https://github.com/contro1-hq/centcom-sdk/blob/main/skills/centcom-js-sdk.md
- Microsoft AGT companion skill: https://github.com/contro1-hq/contro1-microsoft-agent-governance-toolkit-integration/blob/main/skills/contro1-microsoft-agent-governance-toolkit-integration.md
