"""
NNAD (National Notifiable Diseases Surveillance System) Validator

Validates case notification data submissions using Generic v2 MMG standards
Handles both HL7 and CSV formats
"""

from .base_validator import BaseValidator
from utils.validators_common import (
    validate_date_format,
    validate_code_in_list,
    validate_integer,
    check_duplicate_rows
)
from utils.state_codes import VALID_STATE_ABBRS, validate_state_code
import pandas as pd

class NNADValidator(BaseValidator):
    """Validator for NNAD/NNDSS case notification data"""

    # Generic MMG required fields (appear in all disease MMGs)
    REQUIRED_FIELDS = [
        'condition',
        'reporting_jurisdiction',
        'case_status',
        'report_date',
        'illness_onset_date'
    ]

    # Optional common fields
    OPTIONAL_FIELDS = [
        'age_at_case_investigation',
        'age_unit',
        'birth_date',
        'sex',
        'race',
        'ethnicity',
        'country_of_residence',
        'state_of_residence',
        'county_of_residence',
        'hospitalized',
        'died',
        'pregnant',
        'case_investigation_start_date',
        'illness_end_date',
        'outbreak_associated',
        'outbreak_name'
    ]

    # Valid case statuses
    CASE_STATUS_CODES = {
        '410605003': 'Confirmed',
        '2931005': 'Probable',
        '415684004': 'Suspected',
        'PHC1464': 'Not a case'
    }

    # Valid age units
    AGE_UNITS = {'a': 'Years', 'mo': 'Months', 'd': 'Days', 'h': 'Hours'}

    # Valid sex codes
    SEX_CODES = {'M': 'Male', 'F': 'Female', 'U': 'Unknown', 'O': 'Other'}

    def __init__(self):
        super().__init__(
            system_id='nnad',
            system_name='NNAD (NNDSS)',
            description='National Notifiable Diseases Surveillance System case notifications'
        )

    def validate_structure(self, df, result):
        """Validate NNAD file structure"""

        # Normalize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Check required fields
        missing_required = [col for col in self.REQUIRED_FIELDS if col not in df.columns]

        if missing_required:
            result.add_error(
                f"Missing required fields: {', '.join(missing_required)}",
                doc_link='#nnad-completeness-1-1'
            )
            return

        # Log optional fields present
        optional_present = [col for col in self.OPTIONAL_FIELDS if col in df.columns]
        if optional_present:
            result.add_info(f"Optional fields included: {len(optional_present)}/{len(self.OPTIONAL_FIELDS)}")

    def validate_content(self, df, result):
        """Validate NNAD data content"""

        # Jurisdiction validation
        if 'reporting_jurisdiction' in df.columns:
            for idx, jurisdiction in enumerate(df['reporting_jurisdiction']):
                if pd.notna(jurisdiction):
                    state_info = validate_state_code(jurisdiction, 'abbr')
                    if not state_info:
                        result.add_error(
                            f"Invalid jurisdiction code: {jurisdiction}",
                            row=idx+2,
                            field='reporting_jurisdiction'
                        )
                        # Suggest nearby valid codes
                        if len(str(jurisdiction)) == 2:
                            nearby = [s for s in VALID_STATE_ABBRS if s[0] == str(jurisdiction)[0]][:3]
                            result.add_info(f"Did you mean: {', '.join(nearby)}?", row=idx+2)

        # Case status validation
        if 'case_status' in df.columns:
            for idx, status in enumerate(df['case_status']):
                if pd.notna(status):
                    # Convert to string to handle numeric codes
                    status_str = str(status).strip()
                    is_valid, msg = validate_code_in_list(
                        status_str,
                        self.CASE_STATUS_CODES.keys(),
                        "Case status"
                    )
                    if not is_valid:
                        result.add_error(msg, row=idx+2, field='case_status')
                        result.add_info(
                            f"Valid codes: {', '.join([f'{k} ({v})' for k, v in self.CASE_STATUS_CODES.items()])}",
                            row=idx+2
                        )

        # Date validation
        date_fields = ['report_date', 'illness_onset_date', 'birth_date',
                       'case_investigation_start_date', 'illness_end_date']

        for field in date_fields:
            if field in df.columns:
                for idx, date_val in enumerate(df[field]):
                    if pd.notna(date_val) and str(date_val).strip():
                        is_valid, msg = validate_date_format(date_val)
                        if not is_valid:
                            result.add_error(f"{field}: {msg}", row=idx+2, field=field)

        # Age validation
        if 'age_at_case_investigation' in df.columns:
            for idx, age in enumerate(df['age_at_case_investigation']):
                if pd.notna(age):
                    is_valid, msg = validate_integer(age, min_val=0, max_val=120)
                    if not is_valid:
                        result.add_error(
                            f"Invalid age: {msg}",
                            row=idx+2,
                            field='age_at_case_investigation',
                            doc_link='#nnad-accuracy-2-1'
                        )

        # Age unit validation
        if 'age_unit' in df.columns:
            for idx, unit in enumerate(df['age_unit']):
                if pd.notna(unit):
                    is_valid, msg = validate_code_in_list(unit, self.AGE_UNITS.keys(), "Age unit")
                    if not is_valid:
                        result.add_warning(msg, row=idx+2, field='age_unit')

        # Sex validation
        if 'sex' in df.columns:
            for idx, sex in enumerate(df['sex']):
                if pd.notna(sex):
                    is_valid, msg = validate_code_in_list(sex, self.SEX_CODES.keys(), "Sex")
                    if not is_valid:
                        result.add_warning(msg, row=idx+2, field='sex')

    def validate_custom(self, df, result):
        """Custom NNAD validations"""

        # Check for duplicate cases (same jurisdiction + condition + onset date)
        if all(col in df.columns for col in ['reporting_jurisdiction', 'condition', 'illness_onset_date']):
            has_dups, dup_indices, msg = check_duplicate_rows(
                df,
                subset=['reporting_jurisdiction', 'condition', 'illness_onset_date']
            )
            if has_dups:
                result.add_warning(f"Possible duplicate cases: {msg}")

        # Logical date validation: onset before report
        if 'illness_onset_date' in df.columns and 'report_date' in df.columns:
            for idx in range(len(df)):
                onset = df['illness_onset_date'].iloc[idx]
                report = df['report_date'].iloc[idx]

                if pd.notna(onset) and pd.notna(report):
                    try:
                        onset_date = pd.to_datetime(onset)
                        report_date = pd.to_datetime(report)

                        if onset_date > report_date:
                            result.add_error(
                                "Illness onset date cannot be after report date",
                                row=idx+2,
                                field='illness_onset_date',
                                doc_link='#nnad-consistency-3-1'
                            )
                    except:
                        pass  # Already caught in date validation

        # Check hospitalization/death logic
        if 'died' in df.columns and 'hospitalized' in df.columns:
            for idx in range(len(df)):
                died = str(df['died'].iloc[idx]).upper()
                hospitalized = str(df['hospitalized'].iloc[idx]).upper()

                # If died = Yes, should probably have been hospitalized
                if died == 'Y' and hospitalized == 'N':
                    result.add_warning(
                        "Patient died but not hospitalized - verify data",
                        row=idx+2,
                        field='died',
                        doc_link='#nnad-consistency-3-2'
                    )

        # Summary info
        result.add_info(f"Validated {len(df)} case notification(s)")

        if 'condition' in df.columns:
            conditions = df['condition'].value_counts().to_dict()
            result.add_info(f"Conditions: {', '.join([f'{k} ({v})' for k, v in list(conditions.items())[:5]])}")
