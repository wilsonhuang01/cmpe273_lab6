"""Small read-only inventory API for the Kubernetes service-routing lab."""

import os
from pathlib import Path
import socket

from flask import Flask, jsonify

app = Flask(__name__)
STOCK = {"sku-123": 7}
POD_NAME = os.environ.get("POD_NAME", socket.gethostname())
NOT_READY_FILE = Path(os.environ.get("NOT_READY_FILE", "/tmp/inventory-not-ready"))


@app.get("/health")
def health():
    return jsonify(status="ok", service="inventory", pod=POD_NAME)


@app.get("/ready")
def ready():
    is_ready = not NOT_READY_FILE.exists()
    return jsonify(ready=is_ready, pod=POD_NAME), 200 if is_ready else 503


@app.get("/v1/items/<item_id>")
def get_item(item_id):
    if item_id not in STOCK:
        return jsonify(error="item_not_found", pod=POD_NAME), 404
    return jsonify(item_id=item_id, available=STOCK[item_id], pod=POD_NAME)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, threaded=True)
