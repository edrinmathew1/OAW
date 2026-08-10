# ─────────────────────────────────────────────
#  server.py — Flask RESTful Web API Server
#  Provides CRUD endpoints for dataset.json using Python dictionary functions.
# ─────────────────────────────────────────────

import os
import json
from datetime import datetime
from flask import Flask, jsonify, request, make_response

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "dataset.json")

app = Flask(__name__)


# ── Helper functions using Dictionary Operations ────────────────────────────

def load_data() -> list[dict]:
    """Load JSON records from disk as a list of Python dictionaries."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data: list[dict]) -> None:
    """Save list of Python dictionaries back to disk in JSON format."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def find_record_by_id(records: list[dict], record_id: int) -> tuple[int, dict | None]:
    """Demonstrate dictionary iteration & matching."""
    for idx, rec in enumerate(records):
        if rec.get("id") == record_id:
            return idx, rec
    return -1, None


# ── Custom JSON Error Handlers ───────────────────────────────────────────────

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({"error": "Bad Request", "message": str(error)}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({"error": "Not Found", "message": str(error)}), 404)


@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({"error": "Method Not Allowed", "message": str(error)}), 405)


@app.errorhandler(500)
def server_error(error):
    return make_response(jsonify({"error": "Internal Server Error", "message": str(error)}), 500)


# ── RESTful Endpoints (GET, POST, PUT, DELETE) ──────────────────────────────

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "Agent Tools REST API", "timestamp": datetime.now().isoformat()})


@app.route("/api/records", methods=["GET"])
def get_all_records():
    """
    GET - Retrieve all records (with optional ?category= filter).
    """
    records = load_data()
    category = request.args.get("category")
    
    if category:
        # Use dictionary filtering
        records = [r for r in records if r.get("category", "").lower() == category.lower()]
        
    return jsonify({
        "status": "success",
        "count": len(records),
        "records": records
    }), 200


@app.route("/api/records/<int:record_id>", methods=["GET"])
def get_record_by_id(record_id: int):
    """
    GET - Retrieve a single record by ID.
    """
    records = load_data()
    _, record = find_record_by_id(records, record_id)
    
    if not record:
        return jsonify({"error": "Not Found", "message": f"Record with ID {record_id} does not exist."}), 404
        
    return jsonify({"status": "success", "record": record}), 200


@app.route("/api/records", methods=["POST"])
def create_record():
    """
    POST - Create a new record.
    """
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Content-Type must be application/json."}), 400
        
    payload = request.get_json()
    
    # Required dictionary keys check
    required_keys = ["name", "category", "description"]
    missing = [k for k in required_keys if k not in payload or not payload[k]]
    if missing:
        return jsonify({"error": "Bad Request", "message": f"Missing required fields: {', '.join(missing)}"}), 400
        
    records = load_data()
    
    # Generate new ID (max existing ID + 1)
    new_id = max([r.get("id", 0) for r in records], default=0) + 1
    
    # Construct dictionary using dict operations
    new_record = {
        "id": new_id,
        "name": payload.get("name").strip(),
        "category": payload.get("category").strip(),
        "description": payload.get("description").strip(),
        "status": payload.get("status", "Active"),
        "usage_count": int(payload.get("usage_count", 0)),
        "rating": float(payload.get("rating", 4.5)),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    records.append(new_record)
    save_data(records)
    
    return jsonify({
        "status": "created",
        "message": "Record added successfully.",
        "record": new_record
    }), 201


@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id: int):
    """
    PUT - Update an existing record by ID.
    """
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Content-Type must be application/json."}), 400
        
    payload = request.get_json()
    records = load_data()
    idx, existing = find_record_by_id(records, record_id)
    
    if not existing:
        return jsonify({"error": "Not Found", "message": f"Record with ID {record_id} does not exist."}), 404

    # Update dictionary fields using dict.update() or key assignment
    existing["name"] = payload.get("name", existing.get("name"))
    existing["category"] = payload.get("category", existing.get("category"))
    existing["description"] = payload.get("description", existing.get("description"))
    existing["status"] = payload.get("status", existing.get("status"))
    if "usage_count" in payload:
        existing["usage_count"] = int(payload["usage_count"])
    if "rating" in payload:
        existing["rating"] = float(payload["rating"])
    existing["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    records[idx] = existing
    save_data(records)
    
    return jsonify({
        "status": "success",
        "message": f"Record {record_id} updated successfully.",
        "record": existing
    }), 200


@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id: int):
    """
    DELETE - Remove a record by ID.
    """
    records = load_data()
    idx, existing = find_record_by_id(records, record_id)
    
    if not existing:
        return jsonify({"error": "Not Found", "message": f"Record with ID {record_id} does not exist."}), 404

    # Remove item from list using dictionary pop
    deleted_item = records.pop(idx)
    save_data(records)
    
    return jsonify({
        "status": "success",
        "message": f"Record {record_id} deleted successfully.",
        "deleted_record": deleted_item
    }), 200


if __name__ == "__main__":
    print("[SERVER] Starting Agent Tools REST API Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

