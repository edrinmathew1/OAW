# ─────────────────────────────────────────────
#  file_demo.py — File Handling & RegEx Demonstration Script
#  Demonstrates file opening modes (w, r, a, r+, w+), file methods (seek, tell, etc.),
#  file CRUD operations, regex validations, and backup creation.
# ─────────────────────────────────────────────

import os
from file_manager import (
    create_file, read_all_records, append_record, search_record,
    update_record, delete_record, create_backup,
    validate_id, validate_email, validate_date, validate_tool_code,
    DEFAULT_FILE, BACKUP_FILE
)


def print_title(title: str) -> None:
    print("\n" + "=" * 65)
    print(f" [*] {title}")
    print("=" * 65)


def main():
    print_title("LAB ASSIGNMENT — FILE HANDLING & REGEX VALIDATION DEMO")

    # ── Step 1: RegEx Input Validation Demonstration ─────────────────────────
    print_title("1. RegEx Input Validation Demonstrations")
    
    test_cases = [
        ("ID Validation", "101", validate_id("101")),
        ("ID Validation (Invalid)", "abc10", validate_id("abc10")),
        ("Email Validation", "user@oaw.io", validate_email("user@oaw.io")),
        ("Email Validation (Invalid)", "user@com", validate_email("user@com")),
        ("Date Validation", "2026-08-10", validate_date("2026-08-10")),
        ("Date Validation (Invalid)", "10-08-2026", validate_date("10-08-2026")),
        ("Tool Code Validation", "OAW-105", validate_tool_code("OAW-105")),
        ("Tool Code Validation (Invalid)", "tool105", validate_tool_code("tool105")),
    ]

    for label, input_val, result in test_cases:
        status = "PASSED (Valid)" if result else "FAILED (Invalid)"
        print(f"  • {label:<30} Input: '{input_val}' -> {status}")

    # ── Step 2: File Creation (Mode 'w' & writelines()) ───────────────────────
    print_title("2. File Creation (Mode 'w' & writelines())")
    msg = create_file()
    print(msg)

    # ── Step 3: Read Records (Mode 'r' & readlines(), seek(), tell()) ──────────
    print_title("3. Read & Display All Records (Mode 'r' & readlines(), seek(), tell())")
    records = read_all_records()
    print(f"Total lines read: {len(records)}")
    for line in records:
        print(f"  {line.strip()}")

    # ── Step 4: Append Record (Mode 'a' & write()) ────────────────────────────
    print_title("4. Append New Record (Mode 'a' & write())")
    new_rec = "104|OAW-104|Memory Manager|memory@oaw.io|2026-08-10|Active"
    msg_app = append_record(new_rec)
    print(msg_app)

    # Verify append
    records_after_append = read_all_records()
    print(f"Total lines after append: {len(records_after_append)}")
    print(f"  Appended Line: {records_after_append[-1].strip()}")

    # ── Step 5: Search Record (Mode 'r' & tell(), seek(), readline()) ─────────
    print_title("5. Search Record by Key ID (Mode 'r' & seek(), tell())")
    found = search_record("102")
    if found:
        print(f"  [Found Record ID 102]: {found}")
    else:
        print("  Record not found.")

    # ── Step 6: Update Record (Mode 'r+' & seek(), write()) ───────────────────
    print_title("6. Update Record (Mode 'r+' & seek(), write())")
    updated_rec = "102|OAW-102|Code Interpreter (Enhanced)|dev@oaw.io|2026-08-10|Active"
    success = update_record("102", updated_rec)
    print(f"  Update status for ID 102: {'SUCCESS' if success else 'FAILED'}")

    updated_line = search_record("102")
    print(f"  Updated Record Content: {updated_line}")

    # ── Step 7: Delete Record (Mode 'w+' & truncate()) ────────────────────────
    print_title("7. Delete Record (Mode 'w+')")
    del_success = delete_record("103")
    print(f"  Delete status for ID 103: {'SUCCESS' if del_success else 'FAILED'}")
    
    remaining = read_all_records()
    print(f"  Remaining records count: {len(remaining)}")

    # ── Step 8: Create Backup Copy ───────────────────────────────────────────
    print_title("8. Create Data File Backup Copy")
    backup_msg = create_backup()
    print(backup_msg)
    print(f"  Backup File Exists: {os.path.exists(BACKUP_FILE)}")

    print_title("FILE HANDLING & REGEX DEMONSTRATION COMPLETE")


if __name__ == "__main__":
    main()
