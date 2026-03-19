---
name: centcom-n8n
description: Guide for integrating n8n workflows with CENTCOM via HTTP Request and Wait webhook resume.
user_invocable: true
---

# CENTCOM + n8n Skill

Use this skill when a user wants n8n workflow approvals handled by CENTCOM.

## Implementation steps

1. Create request with n8n HTTP Request node.
2. Pause with Wait node (On Webhook Call).
3. Resume via callback and branch by approval result.
4. Keep execution metadata in request `metadata`.

## Short example

```json
{
  "type": "approval",
  "question": "Approve deployment?",
  "context": "n8n workflow requests production deploy approval.",
  "callback_url": "https://your-n8n-host/webhook/centcom-resume"
}
```
