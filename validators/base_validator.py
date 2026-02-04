"""
BaseValidator - Abstract base class for all data stream validators

All specific validators (NNAD, Mumps, NREVSS, etc.) inherit from this class
and implement system-specific validation logic.
"""

from abc import ABC, abstractmethod
import pandas as pd
from models.validation_result import ValidationResult
from utils.validators_common import (
    validate_date_format,
    validate_integer,
    detect_excel_errors,
    detect_placeholder_text,
    check_duplicate_rows
)
from utils.state_codes import validate_state_code

class BaseValidator(ABC):
    """
    Abstract base class for data validators

    Each data stream extends this class and implements:
    - validate_structure(): Check file structure and columns
    - validate_content(): Check data values and logic
    - Additional custom validation methods
    """

    def __init__(self, system_id, system_name, description=''):
        """
        Initialize validator

        Args:
            system_id: Unique system identifier (nnad, mumps, etc.)
            system_name: Human-readable name
            description: Brief description of what this validates
        """
        self.system_id = system_id
        self.system_name = system_name
        self.description = description

    def validate_file(self, file_path, filename):
        """
        Main validation entry point

        Args:
            file_path: Path to uploaded file
            filename: Original filename

        Returns:
            ValidationResult object
        """
        result = ValidationResult(self.system_id, filename)

        try:
            # Read file
            df = self.read_file(file_path, result)

            if df is None:
                result.status = 'failed'
                return result

            result.row_count = len(df)
            result.set_metadata('column_count', len(df.columns))

            # Extract jurisdiction from data for map visualization
            self.extract_jurisdiction(df, result)

            # Run validation phases
            self.validate_structure(df, result)
            self.validate_content(df, result)
            self.validate_quality(df, result)

            # Custom validations (implemented by subclasses)
            self.validate_custom(df, result)

            # Determine final status
            result.determine_status()

        except Exception as e:
            result.add_error(f"Unexpected validation error: {str(e)}")
            result.status = 'failed'

        return result

    def read_file(self, file_path, result):
        """
        Read and parse file

        Args:
            file_path: Path to file
            result: ValidationResult to add errors

        Returns:
            DataFrame or None on error
        """
        try:
            # Try reading as CSV
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.lower().endswith(('.xls', '.xlsx')):
                df = pd.read_excel(file_path)
            elif file_path.lower().endswith('.json'):
                df = pd.read_json(file_path)
            else:
                # Try CSV as default
                df = pd.read_csv(file_path, encoding='utf-8')

            # Check if empty
            if len(df) == 0:
                result.add_error("File is empty (no data rows)")
                return None

            return df

        except UnicodeDecodeError:
            # Try alternate encoding
            try:
                df = pd.read_csv(file_path, encoding='latin-1')
                result.add_warning("File read with latin-1 encoding (expected UTF-8)")
                return df
            except Exception as e:
                result.add_error(f"Could not read file: {str(e)}")
                return None

        except Exception as e:
            result.add_error(f"Error reading file: {str(e)}")
            return None

    @abstractmethod
    def validate_structure(self, df, result):
        """
        Validate file structure (columns, format, etc.)

        Must be implemented by subclasses

        Args:
            df: DataFrame
            result: ValidationResult to add errors
        """
        pass

    @abstractmethod
    def validate_content(self, df, result):
        """
        Validate data content (values, logic, etc.)

        Must be implemented by subclasses

        Args:
            df: DataFrame
            result: ValidationResult to add errors
        """
        pass

    def validate_quality(self, df, result):
        """
        Common data quality checks applied to all systems

        Args:
            df: DataFrame
            result: ValidationResult to add errors
        """
        # Check for completely empty columns
        for col in df.columns:
            if df[col].isna().all():
                result.add_warning(f"Column '{col}' is completely empty")

        # Check for Excel errors
        for col in df.columns:
            for idx, val in enumerate(df[col]):
                is_valid, msg = detect_excel_errors(val)
                if not is_valid:
                    result.add_error(msg, row=idx+2, field=col)

        # Check for suspicious placeholder text in first 100 rows
        sample_size = min(100, len(df))
        for col in df.columns:
            for idx in range(sample_size):
                val = df[col].iloc[idx]
                is_valid, msg = detect_placeholder_text(val)
                if not is_valid:
                    result.add_warning(f"Possible placeholder: {msg}", row=idx+2, field=col)

    def validate_custom(self, df, result):
        """
        Hook for system-specific custom validation

        Optional - subclasses can override

        Args:
            df: DataFrame
            result: ValidationResult to add errors
        """
        pass

    def extract_jurisdiction(self, df, result):
        """
        Extract jurisdiction (state) from data for map visualization.

        Looks for common jurisdiction field names and extracts the most
        frequent valid state code to associate with this submission.

        Args:
            df: DataFrame
            result: ValidationResult to set jurisdiction on
        """
        # Common field names that contain jurisdiction/state info
        jurisdiction_fields = [
            'reporting_jurisdiction',
            'jurisdiction',
            'state',
            'state_code',
            'state_abbr',
            'submitting_state',
            'rpt_state',
            'fips_state'
        ]

        # Normalize column names for matching
        df_cols_lower = {col.lower().replace(' ', '_'): col for col in df.columns}

        for field in jurisdiction_fields:
            if field in df_cols_lower:
                actual_col = df_cols_lower[field]

                # Get non-null values
                values = df[actual_col].dropna().astype(str).str.strip().str.upper()

                if len(values) == 0:
                    continue

                # Find most common value that's a valid state code
                value_counts = values.value_counts()

                for code, count in value_counts.items():
                    # Try as abbreviation first, then as FIPS
                    state_info = validate_state_code(code, 'abbr')
                    if not state_info and code.isdigit():
                        state_info = validate_state_code(code, 'fips')

                    if state_info:
                        result.jurisdiction = state_info['abbr']
                        result.set_metadata('jurisdiction_field', actual_col)
                        result.set_metadata('jurisdiction_name', state_info['name'])
                        return

        # Also try to extract from filename (e.g., "GA_nnad_2026.csv")
        if result.jurisdiction is None:
            filename_parts = result.filename.replace('.csv', '').replace('.xlsx', '').split('_')
            for part in filename_parts:
                part_upper = part.upper()
                state_info = validate_state_code(part_upper, 'abbr')
                if state_info:
                    result.jurisdiction = state_info['abbr']
                    result.set_metadata('jurisdiction_source', 'filename')
                    result.set_metadata('jurisdiction_name', state_info['name'])
                    return

    def validate_required_columns(self, df, required_cols, result):
        """
        Helper: Check that required columns exist

        Args:
            df: DataFrame
            required_cols: List of required column names
            result: ValidationResult to add errors

        Returns:
            True if all present, False otherwise
        """
        actual_cols = set(df.columns)
        missing = [col for col in required_cols if col not in actual_cols]

        if missing:
            result.add_error(f"Missing required columns: {', '.join(missing)}")
            return False

        return True

    def validate_column_types(self, df, column_types, result):
        """
        Helper: Validate column data types

        Args:
            df: DataFrame
            column_types: dict mapping column name to expected type
            result: ValidationResult to add errors
        """
        for col, expected_type in column_types.items():
            if col not in df.columns:
                continue

            # Sample non-null values
            sample = df[col].dropna().head(10)

            for idx, val in sample.items():
                if expected_type == 'int':
                    is_valid, msg = validate_integer(val, allow_null=True)
                    if not is_valid:
                        result.add_error(f"{col}: {msg}", row=idx+2, field=col)
                        break
                elif expected_type == 'date':
                    is_valid, msg = validate_date_format(val)
                    if not is_valid:
                        result.add_error(f"{col}: {msg}", row=idx+2, field=col)
                        break

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.system_id}>"
