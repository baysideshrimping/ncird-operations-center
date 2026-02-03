"""
Comprehensive Data Quality Framework for Public Health Surveillance

Based on ISO 8000, CDC NNDSS guidelines, and WHO surveillance standards.
Implements the Six Data Quality Dimensions:
1. Completeness
2. Accuracy
3. Consistency
4. Validity
5. Timeliness
6. Uniqueness
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re

class DataQualityDimension:
    """Base class for data quality dimension checks"""

    def __init__(self, dimension_name):
        self.dimension_name = dimension_name
        self.checks = []

    def add_check(self, check_name, severity='error'):
        self.checks.append({'name': check_name, 'severity': severity})


class CompletenessChecker:
    """
    Dimension 1: COMPLETENESS
    Extent to which required data elements are present
    """

    @staticmethod
    def check_required_fields_present(df, required_fields):
        """Check if all required fields exist"""
        missing = [f for f in required_fields if f not in df.columns]
        return len(missing) == 0, missing

    @staticmethod
    def check_missing_value_rate(df, field, threshold=0.05):
        """Check if missing values exceed threshold (default 5%)"""
        if field not in df.columns:
            return False, "Field not found"

        missing_rate = df[field].isna().sum() / len(df)
        return missing_rate <= threshold, f"{missing_rate:.1%} missing"

    @staticmethod
    def check_conditional_completeness(df, primary_field, dependent_field):
        """If primary field has value, dependent field must also have value"""
        if primary_field not in df.columns or dependent_field not in df.columns:
            return True, []

        # Where primary has value but dependent doesn't
        mask = df[primary_field].notna() & df[dependent_field].isna()
        problem_rows = df[mask].index.tolist()

        return len(problem_rows) == 0, problem_rows

    @staticmethod
    def detect_empty_required_patterns(df, field):
        """Detect placeholder patterns in required fields"""
        if field not in df.columns:
            return []

        placeholders = ['', ' ', 'n/a', 'na', 'N/A', 'NA', 'null', 'NULL',
                       'none', 'NONE', '?', '??', '???', '.', '..', '...',
                       '-', '--', 'TBD', 'tbd', 'pending', 'PENDING',
                       'unknown', 'UNKNOWN', 'UNK']

        mask = df[field].astype(str).str.strip().str.lower().isin([p.lower() for p in placeholders])
        return df[mask].index.tolist()


class AccuracyChecker:
    """
    Dimension 2: ACCURACY
    Degree to which data correctly represents real-world values
    """

    @staticmethod
    def check_numeric_range(value, min_val, max_val):
        """Check if numeric value is within acceptable range"""
        try:
            num_val = float(value)
            return min_val <= num_val <= max_val
        except:
            return False

    @staticmethod
    def check_age_plausibility(age, age_unit='years'):
        """Check if age is plausible"""
        age_limits = {
            'years': (0, 120),
            'months': (0, 1440),  # 120 years
            'days': (0, 43800),   # 120 years
            'hours': (0, 1051200)  # 120 years
        }

        if age_unit.lower() in ['a', 'y', 'year', 'years']:
            age_unit = 'years'
        elif age_unit.lower() in ['mo', 'month', 'months']:
            age_unit = 'months'
        elif age_unit.lower() in ['d', 'day', 'days']:
            age_unit = 'days'
        elif age_unit.lower() in ['h', 'hr', 'hour', 'hours']:
            age_unit = 'hours'

        limits = age_limits.get(age_unit, (0, 120))
        try:
            age_val = float(age)
            return limits[0] <= age_val <= limits[1], limits
        except:
            return False, limits

    @staticmethod
    def check_percentage_range(value, allow_over_100=False):
        """Check if percentage is in valid range"""
        try:
            pct = float(value)
            if allow_over_100:
                return 0 <= pct <= 999
            return 0 <= pct <= 100
        except:
            return False

    @staticmethod
    def detect_outliers_iqr(df, field, multiplier=3.0):
        """Detect outliers using IQR method"""
        if field not in df.columns or len(df) < 4:
            return []

        try:
            numeric_series = pd.to_numeric(df[field], errors='coerce')
            Q1 = numeric_series.quantile(0.25)
            Q3 = numeric_series.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - multiplier * IQR
            upper_bound = Q3 + multiplier * IQR

            mask = (numeric_series < lower_bound) | (numeric_series > upper_bound)
            return df[mask].index.tolist()
        except:
            return []

    @staticmethod
    def check_precision_excessive(value, max_decimals=2):
        """Check if numeric value has excessive decimal places"""
        try:
            val_str = str(float(value))
            if '.' in val_str:
                decimals = len(val_str.split('.')[1].rstrip('0'))
                return decimals <= max_decimals
            return True
        except:
            return True


class ConsistencyChecker:
    """
    Dimension 3: CONSISTENCY
    Absence of contradictions between related data elements
    """

    @staticmethod
    def check_date_sequence(date1, date2, date1_name, date2_name):
        """Check if date1 comes before or equals date2"""
        try:
            d1 = pd.to_datetime(date1)
            d2 = pd.to_datetime(date2)
            if d1 > d2:
                return False, f"{date1_name} ({date1}) cannot be after {date2_name} ({date2})"
            return True, None
        except:
            return True, None  # Can't validate if parsing fails

    @staticmethod
    def check_cross_field_logic(df, field1, field2, logic_check):
        """Generic cross-field logical consistency check"""
        violations = []
        for idx in range(len(df)):
            val1 = df[field1].iloc[idx]
            val2 = df[field2].iloc[idx]

            if pd.notna(val1) and pd.notna(val2):
                if not logic_check(val1, val2):
                    violations.append(idx)

        return len(violations) == 0, violations

    @staticmethod
    def check_sum_consistency(df, part_fields, total_field):
        """Check if sum of parts equals total"""
        violations = []
        for idx in range(len(df)):
            parts_sum = 0
            all_present = True

            for field in part_fields:
                val = df[field].iloc[idx]
                if pd.isna(val):
                    all_present = False
                    break
                try:
                    parts_sum += float(val)
                except:
                    all_present = False
                    break

            if all_present:
                total_val = df[total_field].iloc[idx]
                try:
                    total = float(total_val)
                    if abs(parts_sum - total) > 0.01:  # Allow small rounding
                        violations.append((idx, parts_sum, total))
                except:
                    pass

        return len(violations) == 0, violations

    @staticmethod
    def check_temporal_consistency(df, value_field, date_field, should_increase=True):
        """Check if values increase/decrease consistently over time"""
        if len(df) < 2:
            return True, []

        df_sorted = df.sort_values(by=date_field)
        violations = []

        for i in range(1, len(df_sorted)):
            prev_val = df_sorted[value_field].iloc[i-1]
            curr_val = df_sorted[value_field].iloc[i]

            if pd.notna(prev_val) and pd.notna(curr_val):
                try:
                    prev = float(prev_val)
                    curr = float(curr_val)

                    if should_increase and curr < prev:
                        violations.append(i)
                    elif not should_increase and curr > prev:
                        violations.append(i)
                except:
                    pass

        return len(violations) == 0, violations


class ValidityChecker:
    """
    Dimension 4: VALIDITY
    Data conforms to defined formats, types, and domains
    """

    @staticmethod
    def check_format_pattern(value, pattern, pattern_name):
        """Check if value matches regex pattern"""
        if pd.isna(value):
            return False, f"Value is missing"

        if re.match(pattern, str(value)):
            return True, None
        return False, f"Does not match {pattern_name} format"

    @staticmethod
    def check_domain_membership(value, valid_domain, domain_name):
        """Check if value is in valid domain"""
        if pd.isna(value):
            return False, "Value is missing"

        if value in valid_domain:
            return True, None

        # Try case-insensitive for strings
        if isinstance(value, str):
            if value.upper() in [str(v).upper() for v in valid_domain]:
                return True, None

        return False, f"Not in valid {domain_name}"

    @staticmethod
    def check_data_type(value, expected_type):
        """Check if value is of expected data type"""
        type_checks = {
            'int': lambda v: isinstance(v, (int, np.integer)) or (isinstance(v, str) and v.isdigit()),
            'float': lambda v: isinstance(v, (int, float, np.number)),
            'string': lambda v: isinstance(v, str),
            'date': lambda v: isinstance(v, (datetime, pd.Timestamp)) or (isinstance(v, str) and len(v) >= 8),
            'bool': lambda v: isinstance(v, (bool, np.bool_))
        }

        check_func = type_checks.get(expected_type, lambda v: True)
        return check_func(value)

    @staticmethod
    def check_code_set_membership(value, code_set, code_system_name):
        """Check if code is in standardized code set (e.g., SNOMED CT)"""
        if pd.isna(value):
            return False, "Code is missing"

        # Convert to string and strip
        value_str = str(value).strip()

        if value_str in code_set:
            return True, None

        return False, f"Not a valid {code_system_name} code"


class TimelinessChecker:
    """
    Dimension 5: TIMELINESS
    Data is available within expected timeframe
    """

    @staticmethod
    def check_reporting_lag(event_date, report_date, max_days):
        """Check if reporting occurred within acceptable window"""
        try:
            event = pd.to_datetime(event_date)
            report = pd.to_datetime(report_date)

            lag_days = (report - event).days

            if lag_days < 0:
                return False, "Report before event (invalid)"
            if lag_days > max_days:
                return False, f"Lag of {lag_days} days exceeds {max_days} day limit"

            return True, None
        except:
            return True, None  # Can't validate if dates invalid

    @staticmethod
    def check_date_recency(date_value, max_age_days):
        """Check if date is recent enough"""
        try:
            date_dt = pd.to_datetime(date_value)
            now = datetime.now()

            age_days = (now - date_dt).days

            if age_days > max_age_days:
                return False, f"Data is {age_days} days old (max {max_age_days})"

            return True, None
        except:
            return True, None

    @staticmethod
    def check_future_date(date_value):
        """Check that date is not in the future"""
        try:
            date_dt = pd.to_datetime(date_value)
            now = datetime.now()

            if date_dt > now:
                return False, f"Date is in the future: {date_value}"

            return True, None
        except:
            return True, None


class UniquenessChecker:
    """
    Dimension 6: UNIQUENESS
    No entity is recorded more than once
    """

    @staticmethod
    def check_primary_key_uniqueness(df, key_fields):
        """Check if combination of key fields is unique"""
        if not all(f in df.columns for f in key_fields):
            return True, []

        duplicates = df[df.duplicated(subset=key_fields, keep=False)]
        return len(duplicates) == 0, duplicates.index.tolist()

    @staticmethod
    def check_exact_duplicates(df):
        """Check for exact duplicate rows"""
        duplicates = df[df.duplicated(keep=False)]
        return len(duplicates) == 0, duplicates.index.tolist()

    @staticmethod
    def detect_suspicious_duplicates(df, check_fields, threshold=0.9):
        """Detect rows that are suspiciously similar"""
        # Simple implementation: check for identical values in key fields
        if not all(f in df.columns for f in check_fields):
            return []

        suspicious = []
        for i in range(len(df)):
            for j in range(i+1, len(df)):
                matches = sum(1 for f in check_fields if df[f].iloc[i] == df[f].iloc[j])
                similarity = matches / len(check_fields)

                if similarity >= threshold:
                    suspicious.append((i, j, similarity))

        return suspicious
