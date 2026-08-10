# ─────────────────────────────────────────────
#  file_manager.py — File Handling & RegEx Validation Module
#
#  Demonstrates:
#    • User-defined functions for Create, Read, Append, Search, Update, Delete, Backup
#    • File Opening Modes: 'w', 'r', 'a', 'r+', 'w+'
#    • File Methods: read(), readline(), readlines(), write(), writelines(), seek(), tell(), close()
#    • RegEx Input Validations (ID, Email, Date, Tool Code)
# ─────────────────────────────────────────────

import os
import re
import shutil
from datetime import datetime

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "data", "records.txt")
BACKUP_FILE = os.path.join(os.path.dirname(__file__), "data", "records_backup.txt")


# ── 1. Input Validation using Regular Expressions ───────────────────────────

def validate_id(record_id: str) -> bool:
    """Validate ID format (1 to 5 digits only)."""
    return bool(re.match(r"^\d{1,5}$", str(record_id).strip()))


def validate_email(email: str) -> bool:
    """Validate Email Address format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, str(email).strip()))


def validate_date(date_str: str) -> bool:
    """Validate Date format (YYYY-MM-DD)."""
    pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
    return bool(re.match(pattern, str(date_str).strip()))


def validate_tool_code(code: str) -> bool:
    """Validate Product/Tool Code (e.g. OAW-101 or TOOL-999)."""
    pattern = r"^[A-Z]{2,5}-\d{3,4}$"
    return bool(re.match(pattern, str(code).strip()))


# ── 2. File Handling Functions & File Modes / Methods ────────────────────────

def create_file(filepath: str = DEFAULT_FILE, sample_records: list[str] | None = None) -> str:
    """
    Operation: Create file & store records.
    Demonstrates Mode 'w' and Method write() / writelines().
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if sample_records is None:
        sample_records = [
            "101|OAW-101|Web Search Tool|admin@oaw.io|2026-08-01|Active\n",
            "102|OAW-102|Code Interpreter|dev@oaw.io|2026-08-02|Active\n",
            "103|OAW-103|API Caller Tool|support@oaw.io|2026-08-03|Active\n",
        ]

    # File Mode 'w' (Write Mode - creates new or truncates existing file)
    f = open(filepath, "w", encoding="utf-8")
    try:
        # File Method writelines()
        f.writelines(sample_records)
    finally:
        # File Method close()
        f.close()

    return f"File '{os.path.basename(filepath)}' created successfully with mode 'w' and writelines()."


def read_all_records(filepath: str = DEFAULT_FILE) -> list[str]:
    """
    Operation: Read & display all records.
    Demonstrates Mode 'r' and Methods read(), readline(), readlines(), tell().
    """
    if not os.path.exists(filepath):
        create_file(filepath)

    # File Mode 'r' (Read Mode)
    f = open(filepath, "r", encoding="utf-8")
    try:
        # File Method tell() — returns current position
        initial_pos = f.tell()
        
        # File Method readlines() — reads all lines into a list
        lines = f.readlines()
        
        # File Method seek() — resets position to beginning
        f.seek(initial_pos)
        
        # File Method readline() — reads single line
        first_line = f.readline()
        
        # File Method read() — reads remaining contents
        full_content = f.read()
        
        return lines
    finally:
        f.close()


def append_record(record_str: str, filepath: str = DEFAULT_FILE) -> str:
    """
    Operation: Append new record.
    Demonstrates Mode 'a' and Method write().
    """
    if not record_str.endswith("\n"):
        record_str += "\n"

    # File Mode 'a' (Append Mode)
    f = open(filepath, "a", encoding="utf-8")
    try:
        # File Method write()
        f.write(record_str)
    finally:
        f.close()

    return f"Record appended successfully with mode 'a' and write()."


def search_record(search_id: str, filepath: str = DEFAULT_FILE) -> str | None:
    """
    Operation: Search for a record using a suitable key (ID).
    Demonstrates Mode 'r' and Methods readline(), tell(), seek().
    """
    if not os.path.exists(filepath):
        return None

    search_id_str = str(search_id).strip()

    f = open(filepath, "r", encoding="utf-8")
    try:
        f.seek(0)
        while True:
            pos = f.tell()  # Track cursor offset
            line = f.readline()
            if not line:
                break
            parts = line.strip().split("|")
            if parts and parts[0] == search_id_str:
                return line.strip()
        return None
    finally:
        f.close()


def update_record(record_id: str, updated_record_str: str, filepath: str = DEFAULT_FILE) -> bool:
    """
    Operation: Update an existing record.
    Demonstrates Mode 'r+' (Read & Write Mode) and Methods seek(), tell(), write().
    """
    if not os.path.exists(filepath):
        return False

    records = read_all_records(filepath)
    updated = False
    new_lines = []

    for line in records:
        parts = line.strip().split("|")
        if parts and parts[0] == str(record_id).strip():
            new_lines.append(updated_record_str.strip() + "\n")
            updated = True
        else:
            new_lines.append(line)

    if updated:
        # File Mode 'r+' (Read/Write update in-place)
        f = open(filepath, "r+", encoding="utf-8")
        try:
            f.seek(0)
            f.writelines(new_lines)
            f.truncate()
        finally:
            f.close()

    return updated


def delete_record(record_id: str, filepath: str = DEFAULT_FILE) -> bool:
    """
    Operation: Delete a record.
    Demonstrates Mode 'w+' (Read & Write Mode with truncation).
    """
    if not os.path.exists(filepath):
        return False

    records = read_all_records(filepath)
    filtered = [l for l in records if l.strip().split("|")[0] != str(record_id).strip()]

    if len(filtered) == len(records):
        return False  # Record ID not found

    # File Mode 'w+' (Read/Write mode — truncates existing content)
    f = open(filepath, "w+", encoding="utf-8")
    try:
        f.writelines(filtered)
        f.seek(0)
        content_after_delete = f.read()
    finally:
        f.close()

    return True


def create_backup(filepath: str = DEFAULT_FILE, backup_filepath: str = BACKUP_FILE) -> str:
    """
    Operation: Create a backup copy of the data file.
    Demonstrates Mode 'r' and 'w' file copy operation.
    """
    if not os.path.exists(filepath):
        create_file(filepath)

    f_in = open(filepath, "r", encoding="utf-8")
    f_out = open(backup_filepath, "w", encoding="utf-8")
    try:
        lines = f_in.readlines()
        f_out.writelines(lines)
    finally:
        f_in.close()
        f_out.close()

    return f"Backup created successfully at '{os.path.basename(backup_filepath)}'."
