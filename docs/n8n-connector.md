# n8n Connector Guide

This guide shows the recommended n8n integration with CENTCOM approvals.

## Recommended flow

1. Use `HTTP Request` node to create CENTCOM request.
2. Use `Wait` node (`On Webhook Call`) to pause.
3. Resume workflow when CENTCOM sends callback.
4. Branch on approval result.

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

## Notes

- Start with built-in nodes before creating custom n8n community nodes.
- Protect resume webhooks with authentication where possible.
