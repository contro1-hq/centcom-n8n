# n8n Connector Guide

This guide shows the recommended n8n integration with Contro1 approvals using Integration Protocol v1.

## Prerequisites

- n8n workflow with external HTTP access
- CENTCOM API key
- Webhook endpoint for resume callbacks

## Authentication setup (required)

Set n8n environment variables:

```bash
CENTCOM_API_KEY=your_centcom_api_key
CENTCOM_BASE_URL=https://api.contro1.com/api/centcom/v1
CENTCOM_WEBHOOK_SECRET=whsec_your_signing_secret
```

In your HTTP Request node, configure:

- Header `Authorization: Bearer {{$env.CENTCOM_API_KEY}}`
- Header `Content-Type: application/json`
- URL: `{{$env.CENTCOM_BASE_URL}}/requests`

## Recommended flow

1. Use `HTTP Request` node to create a protocol v1 request.
2. Use `Wait` node (`On Webhook Call`) to pause.
3. Resume workflow when CENTCOM sends callback.
4. Branch on approval result.

## Starter kit

Use `examples/n8n_callback_proxy.py` for a local callback receiver/proxy.

It includes:

- signature verification for Contro1 callbacks
- forwarding payloads to n8n Wait resume webhook URL
- optional auth bearer when forwarding to n8n

## Node-by-node wiring

1. Trigger node (Webhook/Cron/Manual)
2. Set node (prepare `question`, `context`, metadata)
3. HTTP Request node (`POST /api/centcom/v1/requests`)
4. Wait node (`On Webhook Call`) with auth enabled
5. IF/Switch node:
   - approved -> continue action
   - denied/expired -> fallback branch

## Short request body example

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

## Production notes

- Start with built-in nodes before creating custom n8n community nodes.
- Protect resume webhooks with authentication where possible.
- Store workflow and execution IDs in `metadata`.
- Add timeout handling and explicit denial branch.

## Troubleshooting

- Workflow never resumes: verify `callback_url` is reachable and points to active execution path.
- Wrong branch path: validate response parsing (`approved` or boolean `value`).
- Duplicate requests: generate idempotency key for retried HTTP Request execution.
