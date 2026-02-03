"""
NREVSS (National Respiratory and Enteric Virus Surveillance System) Validator

Validates laboratory-based surveillance data for respiratory viruses
Aggregate weekly reports from participating laboratories
"""

from .base_validator import BaseValidator
from utils.validators_common import (
    validate_date_format,
    validate_integer,
    validate_percentage
)
from utils.state_codes import validate_state_code
import pandas as pd

class NREVSSValidator(BaseValidator):
    """Validator for NREVSS laboratory surveillance data"""

    # Required fields for NREVSS weekly reports
    REQUIRED_FIELDS = [
        'reporting_week',  # CDC Week (e.g., "2026-W04")
        'reporting_lab',  # Laboratory identifier
        'state',  # State abbreviation
        'total_specimens_tested',
        'virus_type'
    ]

    # Virus-specific result fields
    VIRUS_RESULT_FIELDS = [
        'positive_results',
        'negative_results',
        'percent_positive'
    ]

    # Valid virus types
    VIRUS_TYPES = [
        'RSV',  # Respiratory Syncytial Virus
        'Influenza A',
        'Influenza B',
        'Parainfluenza 1',
        'Parainfluenza 2',
        'Parainfluenza 3',
        'Parainfluenza 4',
        'Adenovirus',
        'Rhinovirus',
        'Enterovirus',
        'Human Metapneumovirus',
        'Coronavirus (non-COVID)',
        'SARS-CoV-2'
    ]

    def __init__(self):
        super().__init__(
            system_id='nrevss',
            system_name='DST NREVSS',
            description='National Respiratory and Enteric Virus Surveillance System'
        )

    def validate_structure(self, df, result):
        """Validate NREVSS file structure"""

        # Normalize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Check required fields
        missing = [col for col in self.REQUIRED_FIELDS if col not in df.columns]

        if missing:
            result.add_error(f"Missing required NREVSS fields: {', '.join(missing)}")
            return

        # Check for result fields
        result_present = [col for col in self.VIRUS_RESULT_FIELDS if col in df.columns]
        if len(result_present) == 0:
            result.add_error("No virus result fields found (positive_results, negative_results, percent_positive)")

        result.add_info(f"Result fields present: {', '.join(result_present)}")

    def validate_content(self, df, result):
        """Validate NREVSS data content"""

        # State validation
        if 'state' in df.columns:
            for idx, state in enumerate(df['state']):
                if pd.notna(state):
                    state_info = validate_state_code(state, 'abbr')
                    if not state_info:
                        result.add_error(
                            f"Invalid state code: {state}",
                            row=idx+2,
                            field='state'
                        )

        # Reporting week format validation (YYYY-WNN)
        if 'reporting_week' in df.columns:
            for idx, week in enumerate(df['reporting_week']):
                if pd.notna(week):
                    week_str = str(week).strip()
                    # Check format: YYYY-WNN
                    import re
                    if not re.match(r'^\d{4}-W\d{2}$', week_str):
                        result.add_error(
                            f"Invalid week format: {week_str} (expected YYYY-WNN, e.g., 2026-W04)",
                            row=idx+2,
                            field='reporting_week'
                        )
                else:
                    result.add_error("Reporting week is missing", row=idx+2, field='reporting_week')

        # Virus type validation
        if 'virus_type' in df.columns:
            for idx, virus in enumerate(df['virus_type']):
                if pd.notna(virus):
                    if virus not in self.VIRUS_TYPES:
                        result.add_warning(
                            f"Unexpected virus type: {virus}",
                            row=idx+2,
                            field='virus_type'
                        )
                        result.add_info(f"Common types: {', '.join(self.VIRUS_TYPES[:5])}", row=idx+2)

        # Specimen counts validation
        if 'total_specimens_tested' in df.columns:
            for idx, total in enumerate(df['total_specimens_tested']):
                if pd.notna(total):
                    is_valid, msg = validate_integer(total, min_val=0, max_val=100000)
                    if not is_valid:
                        result.add_error(
                            f"Total specimens: {msg}",
                            row=idx+2,
                            field='total_specimens_tested'
                        )

        # Positive/negative results validation
        if 'positive_results' in df.columns:
            for idx, positive in enumerate(df['positive_results']):
                if pd.notna(positive):
                    is_valid, msg = validate_integer(positive, min_val=0)
                    if not is_valid:
                        result.add_error(
                            f"Positive results: {msg}",
                            row=idx+2,
                            field='positive_results'
                        )

        if 'negative_results' in df.columns:
            for idx, negative in enumerate(df['negative_results']):
                if pd.notna(negative):
                    is_valid, msg = validate_integer(negative, min_val=0)
                    if not is_valid:
                        result.add_error(
                            f"Negative results: {msg}",
                            row=idx+2,
                            field='negative_results'
                        )

        # Percent positive validation
        if 'percent_positive' in df.columns:
            for idx, pct in enumerate(df['percent_positive']):
                if pd.notna(pct):
                    is_valid, msg = validate_percentage(pct)
                    if not is_valid:
                        result.add_error(
                            f"Percent positive: {msg}",
                            row=idx+2,
                            field='percent_positive'
                        )

    def validate_custom(self, df, result):
        """NREVSS-specific custom validations"""

        # Validate positive + negative = total
        if all(col in df.columns for col in ['total_specimens_tested', 'positive_results', 'negative_results']):
            for idx in range(len(df)):
                total = df['total_specimens_tested'].iloc[idx]
                positive = df['positive_results'].iloc[idx]
                negative = df['negative_results'].iloc[idx]

                if pd.notna(total) and pd.notna(positive) and pd.notna(negative):
                    try:
                        total_val = int(total)
                        pos_val = int(positive)
                        neg_val = int(negative)

                        if pos_val + neg_val != total_val:
                            result.add_error(
                                f"Positive ({pos_val}) + Negative ({neg_val}) ≠ Total ({total_val})",
                                row=idx+2,
                                field='total_specimens_tested'
                            )
                    except:
                        pass

        # Validate percent positive calculation
        if all(col in df.columns for col in ['positive_results', 'total_specimens_tested', 'percent_positive']):
            for idx in range(len(df)):
                positive = df['positive_results'].iloc[idx]
                total = df['total_specimens_tested'].iloc[idx]
                reported_pct = df['percent_positive'].iloc[idx]

                if pd.notna(positive) and pd.notna(total) and pd.notna(reported_pct):
                    try:
                        pos_val = int(positive)
                        total_val = int(total)
                        reported_pct_val = float(reported_pct)

                        if total_val > 0:
                            calculated_pct = round((pos_val / total_val) * 100, 1)

                            # Allow small rounding differences
                            if abs(calculated_pct - reported_pct_val) > 0.2:
                                result.add_warning(
                                    f"Percent positive mismatch: Reported {reported_pct_val}%, "
                                    f"Calculated {calculated_pct}%",
                                    row=idx+2,
                                    field='percent_positive'
                                )
                    except:
                        pass

        # Check for suspiciously low specimen counts
        if 'total_specimens_tested' in df.columns:
            for idx, total in enumerate(df['total_specimens_tested']):
                if pd.notna(total):
                    try:
                        total_val = int(total)
                        if total_val < 10:
                            result.add_warning(
                                f"Very low specimen count ({total_val}) - verify data",
                                row=idx+2,
                                field='total_specimens_tested'
                            )
                    except:
                        pass

        # Summary statistics
        if 'virus_type' in df.columns:
            virus_counts = df['virus_type'].value_counts().to_dict()
            result.add_info(f"Virus types in report: {', '.join([f'{k} ({v})' for k, v in virus_counts.items()])}")

        if 'total_specimens_tested' in df.columns:
            try:
                total_specimens = df['total_specimens_tested'].sum()
                result.add_info(f"Total specimens across all reports: {int(total_specimens)}")
            except:
                pass

        if 'state' in df.columns:
            states = df['state'].nunique()
            result.add_info(f"Reporting states: {states}")

        result.add_info(f"Validated {len(df)} laboratory report(s)")
