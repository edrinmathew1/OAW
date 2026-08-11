# ─────────────────────────────────────────────
#  client_demo.py — Python REST API Client Demo
#  Demonstrates GET, POST, PUT, DELETE operations using requests library
#  with complete error handling & user-friendly output formatting.
# ─────────────────────────────────────────────

import sys
import json
import requests

BASE_URL = "http://127.0.0.1:5000/api/records"


def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(f" [*] {title}")
    print("=" * 60)


def print_json(data: dict) -> None:
    print(json.dumps(data, indent=2))


# ── Client Methods ─────────────────────────────────────────────────────────

def test_get_all_records() -> None:
    """1. GET — Retrieve all records."""
    print_section("1. GET — Retrieve All Records")
    try:
        response = requests.get(BASE_URL, timeout=5)
        print(f"HTTP Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Total records retrieved: {data.get('total')}")
            for r in data.get("records", [])[:3]:
                print(f"  * [ID {r['id']}] {r['name']} ({r['category']}) - Status: {r['status']}")
            print("  ... (showing first 3 items)")

        else:
            print_json(response.json())
    except requests.exceptions.ConnectionError:
        print("[x] Error: Could not connect to API server. Ensure server.py is running on http://127.0.0.1:5000")


def test_get_single_record(record_id: int) -> None:
    """2. GET — Retrieve single record by ID."""
    print_section(f"2. GET — Retrieve Record ID {record_id}")
    url = f"{BASE_URL}/{record_id}"
    try:
        response = requests.get(url, timeout=5)
        print(f"HTTP Status Code: {response.status_code}")
        print_json(response.json())
    except requests.exceptions.ConnectionError:
        print("[x] Connection Error")


def test_post_create_record() -> None:
    """3. POST — Create a new record."""
    print_section("3. POST — Create New Tool Record")
    new_tool = {
        "name": "Speech Emotion Analyzer",
        "category": "Multimodal",
        "description": "Detects tone, pitch, and sentiment in user audio inputs.",
        "status": "Beta",
        "usage_count": 25,
        "rating": 4.6
    }
    try:
        response = requests.post(BASE_URL, json=new_tool, timeout=5)
        print(f"HTTP Status Code: {response.status_code}")
        print_json(response.json())
        return response.json().get("record", {}).get("id")
    except requests.exceptions.ConnectionError:
        print("[x] Connection Error")
        return None


def test_put_update_record(record_id: int) -> None:
    """4. PUT — Update existing record."""
    print_section(f"4. PUT — Update Record ID {record_id}")
    url = f"{BASE_URL}/{record_id}"
    update_data = {
        "status": "Active",
        "rating": 4.9,
        "usage_count": 150
    }
    try:
        response = requests.put(url, json=update_data, timeout=5)
        print(f"HTTP Status Code: {response.status_code}")
        print_json(response.json())
    except requests.exceptions.ConnectionError:
        print("[x] Connection Error")


def test_delete_record(record_id: int) -> None:
    """5. DELETE — Remove record by ID."""
    print_section(f"5. DELETE — Remove Record ID {record_id}")
    url = f"{BASE_URL}/{record_id}"
    try:
        response = requests.delete(url, timeout=5)
        print(f"HTTP Status Code: {response.status_code}")
        print_json(response.json())
    except requests.exceptions.ConnectionError:
        print("[x] Connection Error")


# ── Error Handling Demonstrations ──────────────────────────────────────────

def test_error_handling() -> None:
    """6. Error Handling Demonstrations."""
    print_section("6. Error Handling Demonstrations")

    # A. Invalid URL / 404 Missing Resource
    print("\n--- Test A: 404 Missing Resource (Non-existent ID) ---")
    res = requests.get(f"{BASE_URL}/9999", timeout=5)
    print(f"Status Code: {res.status_code}")
    print_json(res.json())

    # B. 400 Bad Request (Missing required JSON fields)
    print("\n--- Test B: 400 Bad Request (Missing required fields) ---")
    bad_payload = {"status": "Active"}
    res = requests.post(BASE_URL, json=bad_payload, timeout=5)
    print(f"Status Code: {res.status_code}")
    print_json(res.json())

    # C. Offline / Invalid Connection
    print("\n--- Test C: Connection Failure (Invalid Host/Port) ---")
    try:
        requests.get("http://127.0.0.1:9999/invalid-endpoint", timeout=2)
    except requests.exceptions.ConnectionError as err:
        print(f"Caught Connection Error cleanly: {err.__class__.__name__} - Server unreachable.")


# ── Main Driver ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(" REST API Python Client Assignment Demonstration")
    print("=" * 60)
    
    # 1. GET All
    test_get_all_records()

    # 2. GET Single
    test_get_single_record(1)

    # 3. POST Create
    created_id = test_post_create_record()

    if created_id:
        # 4. PUT Update
        test_put_update_record(created_id)

        # 5. DELETE
        test_delete_record(created_id)

    # 6. Error Handling
    test_error_handling()

    print_section("Demonstration Finished Successfully")


if __name__ == "__main__":
    main()

