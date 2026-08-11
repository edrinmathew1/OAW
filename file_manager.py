
import os
import re
import shutil
from datetime import datetime

DEFAULT_FILE = os.path.join(os.path.dirname(__file__), "data", "records.txt")
BACKUP_FILE = os.path.join(os.path.dirname(__file__), "data", "records_backup.txt")

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


#File Handling Functions

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

    f = open(filepath, "w", encoding="utf-8")
    try:
        #writelines()
        f.writelines(sample_records)
    finally:
        #close()
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


def process_file_with_prompt(file_content: str, prompt_instruction: str, target_filepath: str = DEFAULT_FILE) -> tuple[str, str]:
    """
    Operation: Process target file content according to natural language prompt instructions.
    Demonstrates: File Opening Modes ('w+', 'a'), Methods (read, write, writelines, seek, tell, close),
                  RegEx processing, backup copy generation, and saving directly to target file.
    """
    filename = os.path.basename(target_filepath)
    dir_name = os.path.dirname(target_filepath) or os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(dir_name, exist_ok=True)
    
    backup_path = os.path.join(dir_name, f"backup_{filename}")

    # 1. Create backup of original file (Mode 'r' & 'w')
    if os.path.exists(target_filepath):
        f_in = open(target_filepath, "r", encoding="utf-8")
        f_bkp = open(backup_path, "w", encoding="utf-8")
        try:
            lines = f_in.readlines()
            f_bkp.writelines(lines)
        finally:
            f_in.close()
            f_bkp.close()

    lines = file_content.splitlines(keepends=True)
    instruction = prompt_instruction.lower()
    modified_lines = []

    # 2. Process transformation instructions
    for line in lines:
        new_line = line

        # Uppercase email or text
        if "uppercase email" in instruction or "uppercase" in instruction:
            new_line = re.sub(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", lambda m: m.group(1).upper(), new_line)
            if "uppercase" in instruction and "email" not in instruction:
                new_line = new_line.upper()

        # Lowercase text
        if "lowercase" in instruction:
            new_line = new_line.lower()

        # Filter / Remove deprecated records
        if ("remove deprecated" in instruction or "delete deprecated" in instruction) and "deprecated" in new_line.lower():
            continue

        # Format dates to YYYY/MM/DD
        if "format date" in instruction or "slash date" in instruction:
            new_line = re.sub(r"(\d{4})-(\d{2})-(\d{2})", r"\1/\2/\3", new_line)

        # Mark active records as Verified
        if "mark active" in instruction or "verify active" in instruction:
            new_line = re.sub(r"\bActive\b", "Active (Verified)", new_line)

        # Custom Search & Replace: "replace X with Y"
        replace_match = re.search(r"replace\s+[\"']?([^\"'\s]+)[\"']?\s+with\s+[\"']?([^\"'\s]+)[\"']?", prompt_instruction, re.IGNORECASE)
        if replace_match:
            old_str, new_str = replace_match.group(1), replace_match.group(2)
            new_line = new_line.replace(old_str, new_str)

        modified_lines.append(new_line)

    # 3. Append / Add new line or record if requested
    if any(kw in instruction for kw in ["append", "add line", "add record", "write line"]):
        add_match = re.search(r"(?:append|add|write)\s+(?:record|line)?\s*[:\-]?\s*(.*)", prompt_instruction, re.IGNORECASE)
        if add_match:
            added_text = add_match.group(1).strip()
            if added_text:
                modified_lines.append(added_text + "\n")
        else:
            modified_lines.append("105|OAW-105|New File Tool Record|added@oaw.io|2026-08-11|Active\n")

    # 4. Save modified content back to target file (Mode 'w+')
    f_mod = open(target_filepath, "w+", encoding="utf-8")
    try:
        f_mod.writelines(modified_lines)
        f_mod.seek(0)
        pos = f_mod.tell()  # Demonstrate tell() method
        final_saved_content = f_mod.read()
    finally:
        f_mod.close()

    status_msg = (
        f"File '{filename}' updated successfully!\n"
        f"• Original Lines: {len(lines)} | Modified Lines: {len(modified_lines)}\n"
        f"• Backup saved to '{os.path.basename(backup_path)}'.\n"
        f"• File pointer offset verified at byte {pos} using seek() and tell()."
    )

    return final_saved_content, status_msg


