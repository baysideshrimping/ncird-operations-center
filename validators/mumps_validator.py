"""
Mumps Disease Surveillance Validator

Validates mumps case data according to Mumps MMG v1.0.2
Includes mumps-specific clinical and laboratory criteria
"""

from .base_validator import BaseValidator
from utils.validators_common import (
    validate_date_format,
    validate_code_in_list,
    validate_integer
)
from utils.state_codes import validate_state_code
import pandas as pd

class MumpsValidator(BaseValidator):
    """Validator for Mumps surveillance data (MMG v1.0.2)"""

    # Mumps MMG required fields
    REQUIRED_FIELDS = [
        'condition',  # Should be "Mumps" or code
        'reporting_jurisdiction',
        'case_status',
        'report_date',
        'illness_onset_date',
        'parotitis',  # Key mumps symptom
        'lab_result'
    ]

    # Mumps-specific clinical fields
    CLINICAL_FIELDS = [
        'parotitis',
        'parotitis_duration_days',
        'orchitis',  # Testicular inflammation
        'oophoritis',  # Ovarian inflammation
        'mastitis',  # Breast inflammation
        'encephalitis',
        'meningitis',
        'pancreatitis',
        'hearing_loss',
        'complications_other'
    ]

    # Mumps lab test fields
    LAB_FIELDS = [
        'lab_result',
        'lab_test_type',
        'specimen_collection_date',
        'lab_result_date',
        'mumps_igm',
        'mumps_pcr',
        'viral_culture'
    ]

    # Valid clinical values (Y/N/U)
    YNU_VALUES = {'Y': 'Yes', 'N': 'No', 'U': 'Unknown'}

    # Valid lab results
    LAB_RESULT_CODES = {
        '10828004': 'Positive',
        '260385009': 'Negative',
        '419984006': 'Inconclusive',
        '260415000': 'Not performed'
    }

    # Valid lab test types
    LAB_TEST_TYPES = {
        'MUMPS_IGM': 'IgM antibody',
        'MUMPS_PCR': 'RT-PCR',
        'VIRAL_CULTURE': 'Viral culture',
        'MUMPS_IGG': 'IgG antibody'
    }

    def __init__(self):
        super().__init__(
            system_id='mumps',
            system_name='Mumps',
            description='Mumps disease surveillance (MMG v1.0.2)'
        )

    def validate_structure(self, df, result):
        """Validate mumps file structure"""

        # Normalize column names
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Check required fields
        missing = [col for col in self.REQUIRED_FIELDS if col not in df.columns]

        if missing:
            result.add_error(f"Missing required mumps fields: {', '.join(missing)}")
            return

        # Check for clinical fields
        clinical_present = [col for col in self.CLINICAL_FIELDS if col in df.columns]
        result.add_info(f"Clinical fields present: {len(clinical_present)}/{len(self.CLINICAL_FIELDS)}")

        # Check for lab fields
        lab_present = [col for col in self.LAB_FIELDS if col in df.columns]
        result.add_info(f"Laboratory fields present: {len(lab_present)}/{len(self.LAB_FIELDS)}")

    def validate_content(self, df, result):
        """Validate mumps data content"""

        # Jurisdiction validation
        if 'reporting_jurisdiction' in df.columns:
            for idx, jurisdiction in enumerate(df['reporting_jurisdiction']):
                if pd.notna(jurisdiction):
                    state_info = validate_state_code(jurisdiction, 'abbr')
                    if not state_info:
                        result.add_error(
                            f"Invalid jurisdiction: {jurisdiction}",
                            row=idx+2,
                            field='reporting_jurisdiction'
                        )

        # Parotitis (key symptom)
        if 'parotitis' in df.columns:
            for idx, parotitis in enumerate(df['parotitis']):
                if pd.notna(parotitis):
                    is_valid, msg = validate_code_in_list(
                        str(parotitis).upper(),
                        self.YNU_VALUES.keys(),
                        "Parotitis"
                    )
                    if not is_valid:
                        result.add_error(msg, row=idx+2, field='parotitis')
                else:
                    result.add_warning("Parotitis value is missing", row=idx+2, field='parotitis')

        # Parotitis duration
        if 'parotitis_duration_days' in df.columns:
            for idx, duration in enumerate(df['parotitis_duration_days']):
                if pd.notna(duration):
                    is_valid, msg = validate_integer(duration, min_val=0, max_val=60)
                    if not is_valid:
                        result.add_error(
                            f"Parotitis duration: {msg}",
                            row=idx+2,
                            field='parotitis_duration_days'
                        )

        # Lab result validation
        if 'lab_result' in df.columns:
            for idx, lab_result in enumerate(df['lab_result']):
                if pd.notna(lab_result):
                    # Convert to string to handle numeric codes
                    lab_result_str = str(lab_result).strip()
                    is_valid, msg = validate_code_in_list(
                        lab_result_str,
                        self.LAB_RESULT_CODES.keys(),
                        "Lab result"
                    )
                    if not is_valid:
                        result.add_error(msg, row=idx+2, field='lab_result')

        # Clinical Y/N/U fields
        ynu_fields = ['orchitis', 'oophoritis', 'mastitis', 'encephalitis',
                      'meningitis', 'pancreatitis', 'hearing_loss']

        for field in ynu_fields:
            if field in df.columns:
                for idx, value in enumerate(df[field]):
                    if pd.notna(value):
                        is_valid, msg = validate_code_in_list(
                            str(value).upper(),
                            self.YNU_VALUES.keys(),
                            field.replace('_', ' ').title()
                        )
                        if not is_valid:
                            result.add_warning(msg, row=idx+2, field=field)

        # Date validation
        date_fields = ['report_date', 'illness_onset_date',
                       'specimen_collection_date', 'lab_result_date']

        for field in date_fields:
            if field in df.columns:
                for idx, date_val in enumerate(df[field]):
                    if pd.notna(date_val) and str(date_val).strip():
                        is_valid, msg = validate_date_format(date_val)
                        if not is_valid:
                            result.add_error(f"{field}: {msg}", row=idx+2, field=field)

    def validate_custom(self, df, result):
        """Mumps-specific custom validations"""

        # Validate parotitis + parotitis duration logic
        if 'parotitis' in df.columns and 'parotitis_duration_days' in df.columns:
            for idx in range(len(df)):
                parotitis = str(df['parotitis'].iloc[idx]).upper()
                duration = df['parotitis_duration_days'].iloc[idx]

                # If parotitis = No, duration should be 0 or empty
                if parotitis == 'N' and pd.notna(duration) and duration > 0:
                    result.add_warning(
                        "Parotitis is No but duration > 0",
                        row=idx+2,
                        field='parotitis_duration_days'
                    )

                # If parotitis = Yes, duration should be present
                if parotitis == 'Y' and (pd.isna(duration) or duration == 0):
                    result.add_warning(
                        "Parotitis is Yes but duration is missing/zero",
                        row=idx+2,
                        field='parotitis_duration_days'
                    )

        # Lab specimen date should be before result date
        if 'specimen_collection_date' in df.columns and 'lab_result_date' in df.columns:
            for idx in range(len(df)):
                collection = df['specimen_collection_date'].iloc[idx]
                result_date = df['lab_result_date'].iloc[idx]

                if pd.notna(collection) and pd.notna(result_date):
                    try:
                        collection_dt = pd.to_datetime(collection)
                        result_dt = pd.to_datetime(result_date)

                        if collection_dt > result_dt:
                            result.add_error(
                                "Specimen collection date after result date",
                                row=idx+2,
                                field='specimen_collection_date'
                            )
                    except:
                        pass

        # Case classification logic
        # Confirmed: Lab-confirmed (positive IgM, PCR, or culture)
        # Probable: Clinical case definition with epidemiological linkage
        if 'case_status' in df.columns and 'lab_result' in df.columns:
            for idx in range(len(df)):
                status = df['case_status'].iloc[idx]
                lab = df['lab_result'].iloc[idx]

                if pd.notna(status) and pd.notna(lab):
                    # Confirmed case should have positive lab result
                    if status == '410605003' and lab != '10828004':  # Confirmed but not positive
                        result.add_warning(
                            "Case is Confirmed but lab result is not Positive",
                            row=idx+2,
                            field='case_status'
                        )

        # Check for mumps-specific complications
        complications = []
        complication_fields = ['orchitis', 'oophoritis', 'mastitis', 'encephalitis',
                               'meningitis', 'pancreatitis', 'hearing_loss']

        for field in complication_fields:
            if field in df.columns:
                yes_count = (df[field].str.upper() == 'Y').sum() if df[field].dtype == 'object' else 0
                if yes_count > 0:
                    complications.append(f"{field}: {yes_count}")

        if complications:
            result.add_info(f"Complications detected: {', '.join(complications)}")

        # Summary
        result.add_info(f"Validated {len(df)} mumps case(s)")

        if 'parotitis' in df.columns:
            parotitis_yes = (df['parotitis'].str.upper() == 'Y').sum() if df['parotitis'].dtype == 'object' else 0
            result.add_info(f"Cases with parotitis: {parotitis_yes}/{len(df)}")
