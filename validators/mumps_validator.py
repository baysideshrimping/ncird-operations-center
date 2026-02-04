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

    # Valid genotype codes (common mumps strains)
    MUMPS_GENOTYPES = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'N', 'UNK']

    # Y/N/U codes
    YNU_CODES = {'Y': 'Yes', 'N': 'No', 'U': 'Unknown'}

    # MMR vaccination dose thresholds
    MMR_FULL_SERIES = 2  # Standard 2-dose MMR series

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
            result.add_error(
                f"Missing required mumps fields: {', '.join(missing)}",
                doc_link='#mumps-completeness-1-1'
            )
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
                        result.add_error(
                            msg,
                            row=idx+2,
                            field='lab_result',
                            doc_link='#mumps-validity-4-1'
                        )

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
                                field='specimen_collection_date',
                                doc_link='#mumps-consistency-3-2'
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

        # Parotitis clinical criteria validations
        self._validate_parotitis_criteria(df, result)

        # Complication sex-specific validations
        self._validate_complications(df, result)

        # MMR vaccination vs case status
        self._validate_vaccination_status(df, result)

        # Laboratory test timing and adequacy
        self._validate_lab_timing(df, result)

        # Genotype data validation
        self._validate_genotype(df, result)

        # Outbreak linkage validation
        self._validate_outbreak_linkage(df, result)

        # Import status validation
        self._validate_import_status(df, result)

        # Summary
        result.add_info(f"Validated {len(df)} mumps case(s)")

        if 'parotitis' in df.columns:
            parotitis_yes = (df['parotitis'].str.upper() == 'Y').sum() if df['parotitis'].dtype == 'object' else 0
            result.add_info(f"Cases with parotitis: {parotitis_yes}/{len(df)}")

    def _validate_parotitis_criteria(self, df, result):
        """Validate parotitis clinical case definition criteria"""

        if 'parotitis_duration_days' not in df.columns:
            return

        for idx in range(len(df)):
            duration = df['parotitis_duration_days'].iloc[idx]

            if pd.notna(duration):
                try:
                    duration_val = int(duration)

                    # Parotitis duration >60 days is implausible (likely data entry error)
                    if duration_val > 60:
                        result.add_error(
                            f"Parotitis duration {duration_val} days is implausible (likely typo)",
                            row=idx+2,
                            field='parotitis_duration_days',
                            doc_link='#mumps-accuracy-2-1'
                        )

                    # Clinical case definition requires ≥2 days parotitis
                    if 'parotitis' in df.columns:
                        parotitis = str(df['parotitis'].iloc[idx]).upper()

                        if parotitis == 'Y' and duration_val < 2:
                            result.add_warning(
                                f"Parotitis duration {duration_val} day(s) does not meet clinical case definition (≥2 days)",
                                row=idx+2,
                                field='parotitis_duration_days',
                                doc_link='#mumps-consistency-3-3'
                            )
                except:
                    pass

    def _validate_complications(self, df, result):
        """Validate sex-specific complications (common submission error)"""

        # Orchitis only valid in males
        if 'orchitis' in df.columns and 'sex' in df.columns:
            for idx in range(len(df)):
                orchitis = str(df['orchitis'].iloc[idx]).upper() if pd.notna(df['orchitis'].iloc[idx]) else ''
                sex = str(df['sex'].iloc[idx]).upper() if pd.notna(df['sex'].iloc[idx]) else ''

                if orchitis == 'Y' and sex == 'F':
                    result.add_error(
                        "Orchitis (testicular inflammation) cannot occur in female patients",
                        row=idx+2,
                        field='orchitis',
                        doc_link='#mumps-consistency-3-4'
                    )

        # Oophoritis only valid in females
        if 'oophoritis' in df.columns and 'sex' in df.columns:
            for idx in range(len(df)):
                oophoritis = str(df['oophoritis'].iloc[idx]).upper() if pd.notna(df['oophoritis'].iloc[idx]) else ''
                sex = str(df['sex'].iloc[idx]).upper() if pd.notna(df['sex'].iloc[idx]) else ''

                if oophoritis == 'Y' and sex == 'M':
                    result.add_error(
                        "Oophoritis (ovarian inflammation) cannot occur in male patients",
                        row=idx+2,
                        field='oophoritis',
                        doc_link='#mumps-consistency-3-4'
                    )

        # Hospitalization logic for severe complications
        if 'hospitalized' in df.columns:
            for idx in range(len(df)):
                hospitalized = str(df['hospitalized'].iloc[idx]).upper() if pd.notna(df['hospitalized'].iloc[idx]) else ''

                # Check for severe complications
                severe_comps = []
                if 'encephalitis' in df.columns and str(df['encephalitis'].iloc[idx]).upper() == 'Y':
                    severe_comps.append('encephalitis')
                if 'meningitis' in df.columns and str(df['meningitis'].iloc[idx]).upper() == 'Y':
                    severe_comps.append('meningitis')
                if 'pancreatitis' in df.columns and str(df['pancreatitis'].iloc[idx]).upper() == 'Y':
                    severe_comps.append('pancreatitis')

                if severe_comps and hospitalized == 'N':
                    result.add_warning(
                        f"Severe complications ({', '.join(severe_comps)}) but not hospitalized - verify",
                        row=idx+2,
                        field='hospitalized',
                        doc_link='#mumps-consistency-3-5'
                    )

    def _validate_vaccination_status(self, df, result):
        """Validate MMR vaccination vs case classification"""

        if 'mmr_doses' not in df.columns or 'case_status' not in df.columns:
            return

        for idx in range(len(df)):
            doses = df['mmr_doses'].iloc[idx]
            status = df['case_status'].iloc[idx]

            if pd.notna(doses) and pd.notna(status):
                try:
                    dose_count = int(doses)
                    status_str = str(status).strip()

                    # Vaccine breakthrough case (≥2 MMR doses + confirmed/probable)
                    if dose_count >= self.MMR_FULL_SERIES and status_str in ['410605003', '2931005']:
                        result.add_info(
                            f"Vaccine breakthrough case ({dose_count} MMR doses, case_status={self.CASE_STATUS_CODES.get(status_str, status_str)})",
                            row=idx+2
                        )

                    # Check vaccination dates vs illness onset
                    if 'mmr_last_dose_date' in df.columns and 'illness_onset_date' in df.columns:
                        vax_date = df['mmr_last_dose_date'].iloc[idx]
                        onset = df['illness_onset_date'].iloc[idx]

                        if pd.notna(vax_date) and pd.notna(onset):
                            try:
                                vax_dt = pd.to_datetime(vax_date)
                                onset_dt = pd.to_datetime(onset)

                                days_since_vax = (onset_dt - vax_dt).days

                                # Vaccine typically takes 2-3 weeks to provide immunity
                                if days_since_vax < 28:
                                    result.add_info(
                                        f"Illness onset {days_since_vax} days after vaccination (insufficient time for immunity)",
                                        row=idx+2
                                    )
                            except:
                                pass
                except:
                    pass

    def _validate_lab_timing(self, df, result):
        """Validate laboratory test timing and specimen adequacy"""

        # IgM timing validation (acute phase only)
        if all(col in df.columns for col in ['lab_test_type', 'specimen_collection_date', 'illness_onset_date']):
            for idx in range(len(df)):
                test_type = str(df['lab_test_type'].iloc[idx]) if pd.notna(df['lab_test_type'].iloc[idx]) else ''
                collection = df['specimen_collection_date'].iloc[idx]
                onset = df['illness_onset_date'].iloc[idx]

                if 'IGM' in test_type.upper() and pd.notna(collection) and pd.notna(onset):
                    try:
                        collection_dt = pd.to_datetime(collection)
                        onset_dt = pd.to_datetime(onset)

                        days_from_onset = (collection_dt - onset_dt).days

                        # IgM collected too early (before day 3)
                        if days_from_onset < 3:
                            result.add_warning(
                                f"IgM specimen collected {days_from_onset} days after onset (may be false negative - optimal: 3-45 days)",
                                row=idx+2,
                                field='specimen_collection_date',
                                doc_link='#mumps-timeliness-5-1'
                            )

                        # IgM collected too late (after day 45)
                        if days_from_onset > 45:
                            result.add_warning(
                                f"IgM specimen collected {days_from_onset} days after onset (may be false negative - optimal: 3-45 days)",
                                row=idx+2,
                                field='specimen_collection_date',
                                doc_link='#mumps-timeliness-5-1'
                            )
                    except:
                        pass

        # PCR specimen type validation
        if 'lab_test_type' in df.columns and 'specimen_type' in df.columns:
            for idx in range(len(df)):
                test_type = str(df['lab_test_type'].iloc[idx]) if pd.notna(df['lab_test_type'].iloc[idx]) else ''
                spec_type = str(df['specimen_type'].iloc[idx]) if pd.notna(df['specimen_type'].iloc[idx]) else ''

                if 'PCR' in test_type.upper():
                    optimal_specimens = ['buccal swab', 'oral fluid', 'saliva', 'parotid duct']

                    if spec_type and not any(opt in spec_type.lower() for opt in optimal_specimens):
                        result.add_info(
                            f"PCR on specimen type '{spec_type}' - optimal specimens: buccal swab, oral fluid",
                            row=idx+2
                        )

    def _validate_genotype(self, df, result):
        """Validate mumps genotype data if provided"""

        if 'genotype' not in df.columns:
            return

        for idx, genotype in enumerate(df['genotype']):
            if pd.notna(genotype):
                genotype_str = str(genotype).strip().upper()

                if genotype_str and genotype_str not in self.MUMPS_GENOTYPES:
                    result.add_warning(
                        f"Non-standard genotype: {genotype} (expected: A-L, N, or UNK)",
                        row=idx+2,
                        field='genotype',
                        doc_link='#mumps-validity-4-3'
                    )

                # Genotype should have positive PCR or culture
                if 'lab_result' in df.columns:
                    lab = df['lab_result'].iloc[idx]
                    if pd.notna(lab):
                        lab_str = str(lab).strip()
                        if lab_str not in ['10828004', '260373001']:  # Not positive/detected
                            result.add_warning(
                                f"Genotype provided but lab result is not Positive/Detected",
                                row=idx+2,
                                field='genotype'
                            )

    def _validate_outbreak_linkage(self, df, result):
        """Validate outbreak association and clustering"""

        if 'outbreak_associated' not in df.columns:
            return

        for idx, outbreak in enumerate(df['outbreak_associated']):
            if pd.notna(outbreak):
                outbreak_str = str(outbreak).upper()

                if outbreak_str not in self.YNU_CODES.keys():
                    result.add_error(
                        f"Invalid outbreak_associated: {outbreak} (must be Y/N/U)",
                        row=idx+2,
                        field='outbreak_associated',
                        doc_link='#mumps-validity-4-4'
                    )

                # If outbreak-associated, outbreak_name should be present
                if outbreak_str == 'Y' and 'outbreak_name' in df.columns:
                    name = df['outbreak_name'].iloc[idx]
                    if pd.isna(name) or not str(name).strip():
                        result.add_warning(
                            "Outbreak-associated but outbreak_name missing",
                            row=idx+2,
                            field='outbreak_name',
                            doc_link='#mumps-completeness-1-3'
                        )

    def _validate_import_status(self, df, result):
        """Validate import status and travel history"""

        if 'import_status' not in df.columns:
            return

        for idx, status in enumerate(df['import_status']):
            if pd.notna(status):
                status_str = str(status).upper()

                valid_import = ['IMP', 'IND', 'INC', 'UNK', 'IMPORTED', 'INDIGENOUS', 'IMPORT-RELATED', 'UNKNOWN']

                if status_str not in valid_import:
                    result.add_warning(
                        f"Non-standard import status: {status} (recommend: IMP/IND/INC/UNK)",
                        row=idx+2,
                        field='import_status',
                        doc_link='#mumps-validity-4-5'
                    )

                # If imported, travel history should be documented
                if status_str in ['IMP', 'IMPORTED'] and 'travel_history' in df.columns:
                    travel = df['travel_history'].iloc[idx]
                    if pd.isna(travel) or not str(travel).strip():
                        result.add_warning(
                            "Import status=Imported but travel_history missing",
                            row=idx+2,
                            field='travel_history',
                            doc_link='#mumps-completeness-1-4'
                        )
