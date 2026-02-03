"""
Common validation utilities shared across validators
Date validation, format checking, pattern matching, etc.
"""

import re
from datetime import datetime
import pandas as pd

def validate_date_format(date_str, format='%Y-%m-%d'):
    """
    Validate date string against format

    Args:
        date_str: Date string to validate
        format: Expected date format

    Returns:
        (is_valid, error_message or None)
    """
    if pd.isna(date_str) or date_str == '':
        return (False, "Date is missing")

    try:
        datetime.strptime(str(date_str), format)
        return (True, None)
    except ValueError:
        return (False, f"Invalid date format. Expected {format}")

def validate_date_range(date_str, min_year=1900, max_year=None):
    """Validate date is within reasonable range"""
    if max_year is None:
        max_year = datetime.now().year + 1

    try:
        date_obj = datetime.strptime(str(date_str), '%Y-%m-%d')
        if date_obj.year < min_year or date_obj.year > max_year:
            return (False, f"Year must be between {min_year} and {max_year}")
        return (True, None)
    except ValueError:
        return (False, "Invalid date")

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, str(email)):
        return (True, None)
    return (False, "Invalid email format")

def validate_phone(phone):
    """Validate phone number"""
    # Remove common formatting
    cleaned = re.sub(r'[^\d]', '', str(phone))
    if len(cleaned) == 10:
        return (True, None)
    elif len(cleaned) == 11 and cleaned[0] == '1':
        return (True, None)
    return (False, "Phone must be 10 digits (or 11 with leading 1)")

def validate_zipcode(zipcode):
    """Validate US ZIP code"""
    pattern = r'^\d{5}(-\d{4})?$'
    if re.match(pattern, str(zipcode).strip()):
        return (True, None)
    return (False, "ZIP code must be 5 digits or 5+4 format")

def detect_excel_errors(value):
    """Detect Excel error values"""
    error_values = ['#REF!', '#VALUE!', '#DIV/0!', '#NAME?', '#N/A', '#NULL!', '#NUM!']
    if str(value).upper() in error_values:
        return (False, f"Excel error detected: {value}")
    return (True, None)

def detect_placeholder_text(value):
    """Detect placeholder text in data"""
    placeholders = [
        'tbd', 'n/a', 'na', 'null', 'none', 'pending', 'unknown',
        'to be determined', 'not available', 'not applicable', '.',
        '-', '--', '---', '?', '??', 'xxx'
    ]
    if str(value).lower().strip() in placeholders:
        return (False, f"Placeholder text detected: {value}")
    return (True, None)

def validate_integer(value, min_val=None, max_val=None, allow_null=False):
    """Validate integer with optional range"""
    if pd.isna(value) or value == '':
        if allow_null:
            return (True, None)
        return (False, "Value is required")

    try:
        int_val = int(float(value))

        if min_val is not None and int_val < min_val:
            return (False, f"Value must be >= {min_val}")

        if max_val is not None and int_val > max_val:
            return (False, f"Value must be <= {max_val}")

        return (True, None)
    except (ValueError, TypeError):
        return (False, "Must be an integer")

def validate_float(value, min_val=None, max_val=None, allow_null=False):
    """Validate float with optional range"""
    if pd.isna(value) or value == '':
        if allow_null:
            return (True, None)
        return (False, "Value is required")

    try:
        float_val = float(value)

        if min_val is not None and float_val < min_val:
            return (False, f"Value must be >= {min_val}")

        if max_val is not None and float_val > max_val:
            return (False, f"Value must be <= {max_val}")

        return (True, None)
    except (ValueError, TypeError):
        return (False, "Must be a number")

def validate_percentage(value, allow_over_100=False, allow_null=False):
    """Validate percentage value"""
    is_valid, msg = validate_float(value, min_val=0, allow_null=allow_null)

    if not is_valid:
        return (is_valid, msg)

    if not allow_null and not pd.isna(value):
        float_val = float(value)
        if not allow_over_100 and float_val > 100:
            return (False, "Percentage cannot exceed 100%")

    return (True, None)

def validate_code_in_list(value, valid_codes, field_name="Value"):
    """Validate that a code is in a list of valid codes"""
    if pd.isna(value) or value == '':
        return (False, f"{field_name} is required")

    if value not in valid_codes:
        codes_str = ', '.join(str(c) for c in sorted(valid_codes)[:10])
        if len(valid_codes) > 10:
            codes_str += f"... ({len(valid_codes)} total codes)"
        return (False, f"Invalid {field_name}. Valid codes: {codes_str}")

    return (True, None)

def find_similar_column_names(actual_col, expected_cols, threshold=0.7):
    """Find similar column names for typo suggestions"""
    actual_lower = actual_col.lower().replace('_', '').replace(' ', '')

    similarities = []
    for expected in expected_cols:
        expected_lower = expected.lower().replace('_', '').replace(' ', '')

        # Calculate simple similarity
        matching_chars = sum(1 for a, b in zip(actual_lower, expected_lower) if a == b)
        max_len = max(len(actual_lower), len(expected_lower))
        similarity = matching_chars / max_len if max_len > 0 else 0

        if similarity >= threshold:
            similarities.append((expected, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)
    return [col for col, _ in similarities]

def check_duplicate_rows(df, subset=None):
    """
    Check for duplicate rows

    Args:
        df: DataFrame to check
        subset: Optional list of columns to check for duplicates

    Returns:
        (has_duplicates, duplicate_indices, message)
    """
    if subset:
        duplicates = df[df.duplicated(subset=subset, keep=False)]
    else:
        duplicates = df[df.duplicated(keep=False)]

    if len(duplicates) > 0:
        dup_indices = duplicates.index.tolist()
        row_nums = [idx + 2 for idx in dup_indices]  # +2 for 1-based + header
        msg = f"Found {len(dup_indices)} duplicate rows: {row_nums[:10]}"
        if len(row_nums) > 10:
            msg += f"... ({len(row_nums)} total)"
        return (True, dup_indices, msg)

    return (False, [], None)

def validate_hl7_message_structure(content):
    """
    Basic HL7 message structure validation

    Args:
        content: HL7 message content (string)

    Returns:
        (is_valid, error_message or None)
    """
    if not content or len(content) < 10:
        return (False, "HL7 message is empty or too short")

    # Check for HL7 segments
    lines = content.split('\n')
    segments = [line for line in lines if line.strip()]

    # Must start with MSH
    if not segments[0].startswith('MSH'):
        return (False, "HL7 message must start with MSH segment")

    # Check segment format
    for i, segment in enumerate(segments[:5]):  # Check first 5 segments
        if not re.match(r'^[A-Z]{3}\|', segment):
            return (False, f"Invalid segment format at line {i+1}")

    return (True, None)

def normalize_column_names(df):
    """
    Normalize column names (remove spaces, lowercase, etc.)

    Args:
        df: DataFrame

    Returns:
        DataFrame with normalized column names
    """
    df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
    return df
