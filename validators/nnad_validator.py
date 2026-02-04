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

    # Valid Y/N/U codes
    YNU_CODES = {'Y': 'Yes', 'N': 'No', 'U': 'Unknown'}

    # Valid pregnancy statuses
    PREGNANCY_STATUS_CODES = {'Y': 'Yes', 'N': 'No', 'U': 'Unknown', 'NA': 'Not Applicable'}

    # Valid trimester codes
    TRIMESTER_CODES = {'1': 'First', '2': 'Second', '3': 'Third', 'U': 'Unknown'}

    # Valid import status codes
    IMPORT_STATUS_CODES = {
        'IMP': 'Imported',
        'IND': 'Import-related',
        'INC': 'Indigenous',
        'UNK': 'Unknown'
    }

    # Valid transmission setting codes
    TRANSMISSION_SETTINGS = {
        'COM': 'Community',
        'HCF': 'Healthcare facility',
        'SCH': 'School/Daycare',
        'HH': 'Household',
        'WRK': 'Workplace',
        'TRV': 'Travel-related',
        'UNK': 'Unknown'
    }

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

        # Pregnancy status validations
        self._validate_pregnancy_status(df, result)

        # Vaccination history validations
        self._validate_vaccination_history(df, result)

        # Case classification logic validations
        self._validate_case_classification(df, result)

        # Epidemiological linkage validations
        self._validate_epi_linkage(df, result)

        # Investigation timeliness validations
        self._validate_investigation_timeliness(df, result)

        # Demographic consistency validations
        self._validate_demographics(df, result)

        # Import and transmission validations
        self._validate_import_transmission(df, result)

        # Summary info
        result.add_info(f"Validated {len(df)} case notification(s)")

        if 'condition' in df.columns:
            conditions = df['condition'].value_counts().to_dict()
            result.add_info(f"Conditions: {', '.join([f'{k} ({v})' for k, v in list(conditions.items())[:5]])}")

    def _validate_pregnancy_status(self, df, result):
        """Validate pregnancy status and related fields"""

        if 'pregnant' not in df.columns:
            return

        for idx in range(len(df)):
            pregnant = str(df['pregnant'].iloc[idx]).upper() if pd.notna(df['pregnant'].iloc[idx]) else ''

            # Validate pregnancy status code
            if pregnant and pregnant not in self.PREGNANCY_STATUS_CODES.keys():
                result.add_error(
                    f"Invalid pregnancy status: {pregnant} (must be Y/N/U/NA)",
                    row=idx+2,
                    field='pregnant',
                    doc_link='#nnad-validity-4-5'
                )

            # Pregnancy only applicable to females
            if 'sex' in df.columns:
                sex = str(df['sex'].iloc[idx]).upper() if pd.notna(df['sex'].iloc[idx]) else ''

                if pregnant == 'Y' and sex == 'M':
                    result.add_error(
                        "Pregnancy status = Yes for male patient",
                        row=idx+2,
                        field='pregnant',
                        doc_link='#nnad-consistency-3-4'
                    )

                if sex == 'F' and pregnant == '':
                    # Check if reproductive age (12-50)
                    if 'age_at_case_investigation' in df.columns:
                        age = df['age_at_case_investigation'].iloc[idx]
                        if pd.notna(age):
                            try:
                                age_val = int(age)
                                if 12 <= age_val <= 50 and not pregnant:
                                    result.add_warning(
                                        f"Pregnancy status missing for female age {age_val} (reproductive age)",
                                        row=idx+2,
                                        field='pregnant',
                                        doc_link='#nnad-completeness-1-5'
                                    )
                            except:
                                pass

            # Validate trimester if pregnant
            if pregnant == 'Y' and 'pregnancy_trimester' in df.columns:
                trimester = str(df['pregnancy_trimester'].iloc[idx]) if pd.notna(df['pregnancy_trimester'].iloc[idx]) else ''

                if not trimester:
                    result.add_warning(
                        "Pregnancy = Yes but trimester is missing",
                        row=idx+2,
                        field='pregnancy_trimester',
                        doc_link='#nnad-completeness-1-5'
                    )
                elif trimester not in self.TRIMESTER_CODES.keys():
                    result.add_error(
                        f"Invalid trimester: {trimester} (must be 1/2/3/U)",
                        row=idx+2,
                        field='pregnancy_trimester',
                        doc_link='#nnad-validity-4-5'
                    )

            # Pregnancy outcome validation
            if pregnant == 'Y' and 'pregnancy_outcome' in df.columns:
                outcome = str(df['pregnancy_outcome'].iloc[idx]) if pd.notna(df['pregnancy_outcome'].iloc[idx]) else ''

                if outcome:
                    valid_outcomes = ['LIVE_BIRTH', 'STILLBIRTH', 'MISCARRIAGE', 'ABORTION', 'ONGOING', 'UNK']
                    if outcome not in valid_outcomes:
                        result.add_warning(
                            f"Non-standard pregnancy outcome: {outcome}",
                            row=idx+2,
                            field='pregnancy_outcome'
                        )

    def _validate_vaccination_history(self, df, result):
        """Validate vaccination history data"""

        # Vaccination dose count validation
        if 'vaccination_doses' in df.columns:
            for idx, doses in enumerate(df['vaccination_doses']):
                if pd.notna(doses):
                    try:
                        dose_count = int(doses)
                        if dose_count < 0 or dose_count > 10:
                            result.add_error(
                                f"Implausible vaccination dose count: {dose_count}",
                                row=idx+2,
                                field='vaccination_doses',
                                doc_link='#nnad-accuracy-2-4'
                            )
                    except:
                        result.add_error(
                            f"Invalid vaccination dose count: {doses}",
                            row=idx+2,
                            field='vaccination_doses'
                        )

        # Vaccination dates validation
        vax_date_fields = ['vaccination_date_1', 'vaccination_date_2', 'vaccination_date_3']
        for field in vax_date_fields:
            if field in df.columns:
                for idx, vax_date in enumerate(df[field]):
                    if pd.notna(vax_date) and str(vax_date).strip():
                        try:
                            vax_dt = pd.to_datetime(vax_date)

                            # Vaccination date must be before illness onset
                            if 'illness_onset_date' in df.columns:
                                onset = df['illness_onset_date'].iloc[idx]
                                if pd.notna(onset):
                                    onset_dt = pd.to_datetime(onset)
                                    if vax_dt > onset_dt:
                                        result.add_error(
                                            f"Vaccination date ({vax_date}) after illness onset ({onset})",
                                            row=idx+2,
                                            field=field,
                                            doc_link='#nnad-consistency-3-5'
                                        )

                            # Vaccination date must be after birth date
                            if 'birth_date' in df.columns:
                                birth = df['birth_date'].iloc[idx]
                                if pd.notna(birth):
                                    birth_dt = pd.to_datetime(birth)
                                    if vax_dt < birth_dt:
                                        result.add_error(
                                            f"Vaccination date before birth date",
                                            row=idx+2,
                                            field=field,
                                            doc_link='#nnad-consistency-3-5'
                                        )
                        except:
                            pass

        # Vaccination status vs case status logic
        if 'vaccination_doses' in df.columns and 'case_status' in df.columns:
            for idx in range(len(df)):
                doses = df['vaccination_doses'].iloc[idx]
                status = df['case_status'].iloc[idx]

                if pd.notna(doses) and pd.notna(status):
                    try:
                        dose_count = int(doses)
                        status_str = str(status).strip()

                        # Fully vaccinated confirmed case = vaccine breakthrough
                        if dose_count >= 2 and status_str == '410605003':
                            result.add_info(
                                f"Vaccine breakthrough case (≥2 doses, confirmed)",
                                row=idx+2
                                        )
                    except:
                        pass

    def _validate_case_classification(self, df, result):
        """Validate case classification logic against clinical/lab criteria"""

        if 'case_status' not in df.columns:
            return

        for idx in range(len(df)):
            status = str(df['case_status'].iloc[idx]).strip() if pd.notna(df['case_status'].iloc[idx]) else ''

            # Confirmed cases should have lab confirmation
            if status == '410605003':  # Confirmed
                has_lab = False

                lab_fields = ['lab_result', 'specimen_collection_date', 'lab_test_type']
                for field in lab_fields:
                    if field in df.columns:
                        if pd.notna(df[field].iloc[idx]) and str(df[field].iloc[idx]).strip():
                            has_lab = True
                            break

                if not has_lab:
                    result.add_warning(
                        "Confirmed case without laboratory data - verify classification",
                        row=idx+2,
                        field='case_status',
                        doc_link='#nnad-consistency-3-6'
                    )

            # Probable cases should have epi linkage or clinical criteria
            if status == '2931005':  # Probable
                has_epi_link = False

                if 'outbreak_associated' in df.columns:
                    outbreak = str(df['outbreak_associated'].iloc[idx]).upper() if pd.notna(df['outbreak_associated'].iloc[idx]) else ''
                    if outbreak == 'Y':
                        has_epi_link = True

                if 'contact_to_case' in df.columns:
                    contact = str(df['contact_to_case'].iloc[idx]).upper() if pd.notna(df['contact_to_case'].iloc[idx]) else ''
                    if contact == 'Y':
                        has_epi_link = True

                # If neither epi link nor lab, warn
                if not has_epi_link:
                    result.add_info(
                        "Probable case: verify epidemiological linkage documented",
                        row=idx+2
                    )

    def _validate_epi_linkage(self, df, result):
        """Validate epidemiological linkage and outbreak data"""

        # Outbreak association validation
        if 'outbreak_associated' in df.columns:
            for idx, outbreak in enumerate(df['outbreak_associated']):
                if pd.notna(outbreak):
                    outbreak_str = str(outbreak).upper()

                    if outbreak_str not in self.YNU_CODES.keys():
                        result.add_error(
                            f"Invalid outbreak_associated: {outbreak} (must be Y/N/U)",
                            row=idx+2,
                            field='outbreak_associated',
                            doc_link='#nnad-validity-4-6'
                        )

                    # If outbreak = Yes, outbreak_name should be present
                    if outbreak_str == 'Y' and 'outbreak_name' in df.columns:
                        name = df['outbreak_name'].iloc[idx]
                        if pd.isna(name) or not str(name).strip():
                            result.add_warning(
                                "Outbreak-associated but outbreak_name is missing",
                                row=idx+2,
                                field='outbreak_name',
                                doc_link='#nnad-completeness-1-6'
                            )

    def _validate_investigation_timeliness(self, df, result):
        """Validate investigation timeliness metrics"""

        # Report lag: onset to report
        if 'illness_onset_date' in df.columns and 'report_date' in df.columns:
            for idx in range(len(df)):
                onset = df['illness_onset_date'].iloc[idx]
                report = df['report_date'].iloc[idx]

                if pd.notna(onset) and pd.notna(report):
                    try:
                        onset_dt = pd.to_datetime(onset)
                        report_dt = pd.to_datetime(report)

                        lag_days = (report_dt - onset_dt).days

                        if lag_days > 14:
                            result.add_warning(
                                f"Reporting lag = {lag_days} days (>14 days may delay outbreak detection)",
                                row=idx+2,
                                field='report_date',
                                doc_link='#nnad-timeliness-5-4'
                            )
                    except:
                        pass

        # Investigation lag: report to investigation start
        if 'report_date' in df.columns and 'case_investigation_start_date' in df.columns:
            for idx in range(len(df)):
                report = df['report_date'].iloc[idx]
                invest_start = df['case_investigation_start_date'].iloc[idx]

                if pd.notna(report) and pd.notna(invest_start):
                    try:
                        report_dt = pd.to_datetime(report)
                        invest_dt = pd.to_datetime(invest_start)

                        invest_lag = (invest_dt - report_dt).days

                        if invest_lag > 3:
                            result.add_warning(
                                f"Investigation started {invest_lag} days after report (recommend ≤3 days)",
                                row=idx+2,
                                field='case_investigation_start_date',
                                doc_link='#nnad-timeliness-5-4'
                            )
                    except:
                        pass

    def _validate_demographics(self, df, result):
        """Validate demographic data consistency"""

        # Age-sex consistency for certain conditions
        if 'age_at_case_investigation' in df.columns and 'sex' in df.columns and 'condition' in df.columns:
            for idx in range(len(df)):
                age = df['age_at_case_investigation'].iloc[idx]
                sex = str(df['sex'].iloc[idx]).upper() if pd.notna(df['sex'].iloc[idx]) else ''
                condition = str(df['condition'].iloc[idx]) if pd.notna(df['condition'].iloc[idx]) else ''

                if pd.notna(age):
                    try:
                        age_val = int(age)

                        # Congenital conditions in adults
                        congenital_conditions = ['Congenital Rubella', 'Congenital Syphilis']
                        if any(cond in condition for cond in congenital_conditions) and age_val > 2:
                            result.add_warning(
                                f"Congenital condition in adult (age {age_val})",
                                row=idx+2,
                                field='condition',
                                doc_link='#nnad-consistency-3-7'
                            )
                    except:
                        pass

        # Residence jurisdiction validation
        if 'reporting_jurisdiction' in df.columns and 'state_of_residence' in df.columns:
            for idx in range(len(df)):
                report_jur = df['reporting_jurisdiction'].iloc[idx]
                res_state = df['state_of_residence'].iloc[idx]

                if pd.notna(report_jur) and pd.notna(res_state):
                    if report_jur != res_state:
                        result.add_info(
                            f"Patient resides in {res_state} but reported by {report_jur}",
                            row=idx+2
                        )

    def _validate_import_transmission(self, df, result):
        """Validate import status and transmission categories"""

        # Import status validation
        if 'import_status' in df.columns:
            for idx, status in enumerate(df['import_status']):
                if pd.notna(status):
                    status_str = str(status).upper()

                    if status_str not in self.IMPORT_STATUS_CODES.keys():
                        result.add_error(
                            f"Invalid import status: {status}",
                            row=idx+2,
                            field='import_status',
                            doc_link='#nnad-validity-4-7'
                        )

                    # If imported, country should be present
                    if status_str == 'IMP' and 'country_of_exposure' in df.columns:
                        country = df['country_of_exposure'].iloc[idx]
                        if pd.isna(country) or not str(country).strip():
                            result.add_warning(
                                "Import status = Imported but country_of_exposure missing",
                                row=idx+2,
                                field='country_of_exposure',
                                doc_link='#nnad-completeness-1-7'
                            )

        # Transmission setting validation
        if 'transmission_setting' in df.columns:
            for idx, setting in enumerate(df['transmission_setting']):
                if pd.notna(setting):
                    setting_str = str(setting).upper()

                    if setting_str not in self.TRANSMISSION_SETTINGS.keys():
                        result.add_warning(
                            f"Non-standard transmission setting: {setting}",
                            row=idx+2,
                            field='transmission_setting'
                        )
