"""Local proxy for forwarding Contro1 callbacks to n8n Wait webhook resume URL."""

from __future__ import annotations

import json
import os

import requests
from centcom import verify_webhook
from dotenv import load_dotenv
from flask import Flask, jsonify, request

load_dotenv()

app = Flask(__name__)

CENTCOM_WEBHOOK_SECRET = os.environ["CENTCOM_WEBHOOK_SECRET"]
N8N_RESUME_URL = os.environ["N8N_RESUME_URL"]
N8N_RESUME_AUTH_TOKEN = os.environ.get("N8N_RESUME_AUTH_TOKEN", "")
PORT = int(os.environ.get("PROXY_PORT", "8083"))


@app.post("/centcom-callback")
def centcom_callback():
    raw_body = request.get_data(as_text=True)
    signature = request.headers.get("X-CentCom-Signature", "")
    timestamp = request.headers.get("X-CentCom-Timestamp", "")

    if not verify_webhook(raw_body, signature, timestamp, CENTCOM_WEBHOOK_SECRET):
        return jsonify({"error": "invalid signature"}), 401

    payload = json.loads(raw_body)
    headers = {"Content-Type": "application/json"}
    if N8N_RESUME_AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {N8N_RESUME_AUTH_TOKEN}"

    forwarded = requests.post(N8N_RESUME_URL, headers=headers, json=payload, timeout=10)

    return jsonify(
        {
            "status": "forwarded",
            "n8n_status_code": forwarded.status_code,
            "request_id": payload.get("request_id"),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
