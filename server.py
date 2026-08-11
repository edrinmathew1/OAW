# ─────────────────────────────────────────────
#  server.py — Flask REST API Server (Requirement #5)
#
#  Exposes URL endpoints for:
#    • GET /api/status          — Server & system health status
#    • GET /api/records         — Retrieve dataset records
#    • POST /api/records        — Add new record (Returns 201 Created)
#    • PUT /api/records/<id>    — Update existing record
#    • DELETE /api/records/<id> — Remove a record
#    • GET /api/users           — Retrieve registered users
#    • POST /api/users          — Register new user (Returns 201 Created)
#
#  Features custom JSON error handlers for 400, 404, 405, 500 status codes.
# ─────────────────────────────────────────────

import os
import json
from flask import Flask, jsonify, request

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
USER_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")


# ── Helper functions for JSON file operations ─────────────────────────────

def read_json_file(filepath: str, default_val: list | dict) -> list | dict:
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val


def write_json_file(filepath: str, data: list | dict) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── Custom Error Handlers (Requirement #5) ─────────────────────────────────

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad Request", "message": str(error.description)}), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found", "message": "The requested resource or endpoint does not exist."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed", "message": "The HTTP method is not supported for this endpoint."}), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal Server Error", "message": "An unhandled server error occurred."}), 500


# ── API Endpoints ──────────────────────────────────────────────────────────

@app.route("/api/status", methods=["GET"])
def get_status():
    records = read_json_file(DATA_FILE, [])
    users = read_json_file(USER_FILE, {})
    return jsonify({
        "status": "online",
        "service": "Observable Agent Runtime REST API",
        "records_count": len(records),
        "users_count": len(users)
    }), 200


@app.route("/api/records", methods=["GET"])
def get_records():
    records = read_json_file(DATA_FILE, [])
    return jsonify({"status": "success", "total": len(records), "records": records}), 200


@app.route("/api/records/<int:record_id>", methods=["GET"])
def get_record_by_id(record_id: int):
    records = read_json_file(DATA_FILE, [])
    record = next((r for r in records if r.get("id") == record_id), None)
    if not record:
        return jsonify({"error": "Not Found", "message": f"Record with ID {record_id} not found."}), 404
    return jsonify({"status": "success", "record": record}), 200


@app.route("/api/records", methods=["POST"])
def add_record():
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Request payload must be JSON."}), 400

    data = request.get_json()
    name = data.get("name")
    category = data.get("category")
    description = data.get("description")

    if not name or not category or not description:
        return jsonify({"error": "Bad Request", "message": "Missing required fields: 'name', 'category', 'description'."}), 400

    records = read_json_file(DATA_FILE, [])
    new_id = max([r.get("id", 0) for r in records], default=100) + 1

    new_record = {
        "id": new_id,
        "name": name,
        "category": category,
        "description": description,
        "status": data.get("status", "Active"),
        "usage_count": data.get("usage_count", 0),
        "rating": data.get("rating", 4.5)
    }

    records.append(new_record)
    write_json_file(DATA_FILE, records)

    return jsonify({"status": "created", "message": f"Record '{name}' created.", "record": new_record}), 201


@app.route("/api/records/<int:record_id>", methods=["PUT"])
def update_record(record_id: int):
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Request payload must be JSON."}), 400

    data = request.get_json()
    records = read_json_file(DATA_FILE, [])
    record = next((r for r in records if r.get("id") == record_id), None)

    if not record:
        return jsonify({"error": "Not Found", "message": f"Record with ID {record_id} not found."}), 404

    record.update({
        "name": data.get("name", record["name"]),
        "category": data.get("category", record["category"]),
        "description": data.get("description", record["description"]),
        "status": data.get("status", record["status"]),
        "usage_count": data.get("usage_count", record["usage_count"]),
        "rating": data.get("rating", record["rating"])
    })

    write_json_file(DATA_FILE, records)
    return jsonify({"status": "success", "message": f"Record ID {record_id} updated.", "record": record}), 200


@app.route("/api/records/<int:record_id>", methods=["DELETE"])
def delete_record(record_id: int):
    records = read_json_file(DATA_FILE, [])
    updated_records = [r for r in records if r.get("id") != record_id]

    if len(records) == len(updated_records):
        return jsonify({"error": "Not Found", "message": f"Record with ID {record_id} not found."}), 404

    write_json_file(DATA_FILE, updated_records)
    return jsonify({"status": "success", "message": f"Record ID {record_id} deleted."}), 200


# ── Users API Endpoints ───────────────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def get_users():
    users = read_json_file(USER_FILE, {})
    # Strip passwords before returning
    safe_users = {
        username: {k: v for k, v in info.items() if k != "password"}
        for username, info in users.items()
    }
    return jsonify({"status": "success", "total": len(safe_users), "users": safe_users}), 200


@app.route("/api/users", methods=["POST"])
def register_user_api():
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Request payload must be JSON."}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    full_name = data.get("full_name", username)
    email = data.get("email", "")

    if not username or not password:
        return jsonify({"error": "Bad Request", "message": "Missing 'username' or 'password'."}), 400

    users = read_json_file(USER_FILE, {})
    if username in users:
        return jsonify({"error": "Conflict", "message": f"User '{username}' already exists."}), 400

    users[username] = {
        "full_name": full_name,
        "email": email,
        "password": password,
        "phone": data.get("phone", ""),
        "dev_key": data.get("dev_key", "DEV-1001")
    }

    write_json_file(USER_FILE, users)
    return jsonify({"status": "created", "message": f"User '{username}' registered.", "username": username}), 201


if __name__ == "__main__":
    print("[SERVER] Starting OAW REST API Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)

