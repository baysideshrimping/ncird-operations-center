# Data Quality Enhancements - NCIRD Operations Center

## 🎯 Comprehensive Data Quality Framework Implemented

Based on research from:
- **CDC NNDSS Data Quality Guidelines** - Message Validation, Processing, and Provisioning System (MVPS)
- **ISO 8000** - International standard for data quality
- **WHO Surveillance Standards** - Public health data quality dimensions
- **HL7 Best Practices** - Healthcare data validation standards
- **CLIA Requirements** - Laboratory data quality and specimen integrity

---

## 📊 Six Data Quality Dimensions

### 1. **COMPLETENESS** ✓
*"All required data elements are present"*

#### New Validations Added:
- **Required Field Existence**: Verify all mandatory columns present
- **Missing Value Rate Monitoring**: Track % of missing data per field (threshold: 5%)
- **Placeholder Detection**: Identify fake data (N/A, TBD, unknown, ---, ???, pending, etc.)
- **Conditional Completeness**: If Field A has value, Field B must also (e.g., hospitalized=Y requires admission_date)
- **Empty String Detection**: Catch spaces, dots, dashes masquerading as data
- **Completeness Scoring**: Calculate overall data completeness percentage

#### Impact:
- Prevents submission of incomplete records
- Ensures downstream analysis has sufficient data
- Identifies systematic collection gaps

---

### 2. **ACCURACY** 🎯
*"Data values correctly represent real-world information"*

#### New Validations Added:
- **Age Plausibility Checks**:
  - 0-120 years (biological maximum)
  - Age unit validation (years, months, days, hours)
  - Age-condition correlation (pediatric vs adult diseases)

- **Numeric Range Validation**:
  - Lab values within physiological ranges
  - Counts cannot be negative
  - Population sizes within realistic bounds

- **Percentage Validation**:
  - 0-100% for proportions
  - Allows >100 for rates (e.g., per 100,000 population)

- **Statistical Outlier Detection**:
  - IQR method (3x interquartile range)
  - Flags extreme values for review
  - Distinguishes errors from genuine outliers

- **Precision Validation**:
  - Excessive decimals (>2 for %, >4 for lab values) flagged
  - Prevents false precision

- **Magnitude Checks**:
  - 50M+ numerator = suspicious
  - Population >100M = data entry error likely
  - Specimen counts >100,000/week = verify

#### Impact:
- Catches data entry errors (typos, decimal point shifts)
- Identifies biologically implausible values
- Improves confidence in epidemiological analysis

---

### 3. **CONSISTENCY** 🔗
*"No contradictions between related data elements"*

#### New Validations Added:
- **Temporal Consistency**:
  - Birth date < onset date < report date < investigation date
  - Specimen collection < lab result date
  - Death date ≥ all other dates

- **Cross-Field Logic**:
  - If died=Y but hospitalized=N → Warning (unusual)
  - If parotitis=N but duration=5 days → Inconsistent
  - If positive lab but case=Not a case → Verify
  - Numerator ≤ Population (always)

- **Sum Validation**:
  - Age groups sum to total (e.g., 0-17y + 18-64y + 65+ = All adults)
  - Positive + Negative = Total specimens
  - Rollup calculations verified

- **Temporal Monotonicity**:
  - Cumulative counts never decrease month-to-month
  - Population shouldn't swing >20%

- **Logical Relationships**:
  - Can't vaccinate zero population
  - 100% vaccination rate = suspicious (review)
  - Deceased patients should have diagnosis date

#### Impact:
- Prevents contradictory information
- Ensures data tells coherent story
- Identifies logic errors in data collection

---

### 4. **VALIDITY** ✔️
*"Data conforms to defined formats, types, and domains"*

#### New Validations Added:
- **Code Set Validation**:
  - SNOMED CT codes (case status, lab results)
  - ICD-10 codes (if used)
  - LOINC codes (lab tests)
  - UCUM units (measurements)

- **Format Patterns**:
  - CDC Week: YYYY-WNN (e.g., 2026-W04)
  - Date: YYYY-MM-DD (ISO 8601)
  - Phone: 10-digit US format
  - ZIP: 5-digit or ZIP+4
  - Email: RFC 5322 compliant

- **Data Type Enforcement**:
  - Integers where required (counts, IDs)
  - Floats for measurements
  - Strings for text fields
  - Dates for temporal fields

- **Domain Membership**:
  - State codes: 50 states + 6 territories
  - Sex: M, F, U, O (not male/female/1/2)
  - Y/N/U fields strictly enforced
  - Virus types from recognized list

- **Controlled Vocabulary**:
  - Condition names match NNDSS list
  - Lab test names from standard panels
  - Vaccination products from CDC CVX codes

#### Impact:
- Ensures interoperability
- Enables automated processing
- Prevents downstream system errors

---

### 5. **TIMELINESS** ⏱️
*"Data available within expected timeframe"*

#### New Validations Added:
- **Reporting Lag Monitoring**:
  - Onset → Report: Warn if >7 days (varies by disease)
  - Report → Investigation: Warn if >3 days
  - Outbreak cases: 24-hour reporting window

- **Date Recency Validation**:
  - Future dates flagged as errors
  - Very old dates (>2 years) generate warnings
  - Stale data alerts for pending submissions

- **Submission Window Compliance**:
  - Monthly submissions due by 15th of following month
  - Weekly lab reports due within 5 business days
  - Provisional → Final data: <90 days

- **Seasonal Appropriateness**:
  - Flu season vs off-season data patterns
  - RSV seasonality checks
  - Unexpected disease occurrence alerts

#### Impact:
- Ensures timely public health response
- Identifies reporting delays
- Supports outbreak detection

---

### 6. **UNIQUENESS** 🔑
*"No entity recorded more than once"*

#### New Validations Added:
- **Primary Key Uniqueness**:
  - No duplicate (jurisdiction + condition + onset date + patient ID)
  - No duplicate (lab + week + virus type)
  - Case IDs must be unique

- **Exact Duplicate Detection**:
  - Identical rows flagged
  - Likely copy-paste errors

- **Near-Duplicate Detection**:
  - 90%+ similarity across key fields
  - May indicate data entry variations
  - Potential duplicate patients

- **Temporal Duplicate Checking**:
  - Same patient, condition within 30 days
  - May be re-submission vs new episode

- **Cross-Submission Deduplication**:
  - Track cases across multiple submissions
  - Identify duplicates spanning files

#### Impact:
- Prevents double-counting cases
- Accurate incidence calculations
- Reduces data redundancy

---

## 🏥 Domain-Specific Quality Checks

### Laboratory Data (NREVSS, PHLIP)
Based on CLIA quality control standards:

- **Specimen Integrity**:
  - Collection → Transport → Processing timeline
  - Temperature chain verification
  - Specimen volume adequacy

- **Quality Control**:
  - Positive/Negative controls documented
  - Calibration records current
  - Proficiency testing results

- **Result Validation**:
  - Critical values flagged
  - Delta checks (change from previous)
  - Panic values require callback

- **Chain of Custody**:
  - Specimen ID integrity
  - Accessioning verified
  - Result-specimen linkage confirmed

### Case Surveillance (NNAD, Mumps)
Based on CDC MVPS standards:

- **Case Definition Compliance**:
  - Clinical criteria met
  - Laboratory criteria met
  - Epidemiological linkage verified

- **Classification Logic**:
  - Confirmed cases: lab-confirmed
  - Probable cases: clinical + epi link
  - Suspect cases: clinical only
  - Not a case: doesn't meet criteria

- **Completeness by Case Class**:
  - Confirmed: Lab results required
  - Probable: Higher data completeness expected
  - Suspect: Minimal required fields

- **Outbreak Context**:
  - Outbreak-associated cases linked
  - Index case identified
  - Transmission chain documented

---

## 📈 Quality Metrics Dashboard

### New Metrics Calculated:
1. **Completeness Score**: % of required fields with valid data
2. **Accuracy Score**: % of values within plausible ranges
3. **Consistency Score**: % of records passing cross-field checks
4. **Validity Score**: % conforming to formats/codes
5. **Timeliness Score**: % reported within expected window
6. **Uniqueness Score**: % of records that are unique

### Overall Data Quality Index (DQI):
```
DQI = (Completeness + Accuracy + Consistency + Validity + Timeliness + Uniqueness) / 6
```

Scoring:
- 95-100% = Excellent
- 90-94% = Good
- 85-89% = Acceptable
- 80-84% = Needs Improvement
- <80% = Poor (submission at risk)

---

## 🛠️ Implementation Status

### ✅ Completed:
- Comprehensive data quality framework module (`utils/data_quality_framework.py`)
- Enhanced documentation page with collapsible sections
- Six dimension organization
- Search and filter functionality
- Code drill-down capability

### 🚧 In Progress:
- Integrating framework into existing validators
- Adding dimension-specific error messages
- Quality scoring calculation
- Dashboard metrics display

### 📋 Next Steps:
1. Update NNAD validator with all 6 dimensions
2. Update Mumps validator with all 6 dimensions
3. Update NREVSS validator with all 6 dimensions
4. Add quality score cards to dashboard
5. Create data quality reports
6. Implement trend analysis

---

## 📚 Sources & Standards

- [CDC NNDSS Validation Process](https://www.cdc.gov/nndss/in-action/validation-process.html)
- [CDC Message Validation System (MVPS)](https://www.cdc.gov/nndss/technical-resource-center/mvps.html)
- [HL7 Data Quality Best Practices](https://rhapsody.health/blog/complete-guide-to-hl7-standards/)
- [ISO 8000 Data Quality Standards](https://www.dataversity.net/data-quality-dimensions/)
- [CLIA Laboratory Requirements](https://www.cms.gov/regulations-and-guidance/legislation/clia)
- [CDC Public Health Data Strategy 2025-2026](https://www.cdc.gov/public-health-data-strategy/php/about/phds-milestones-2025-and-2026.html)

---

## 💡 Benefits for NCIRD Demo

1. **Industry Standard**: Based on ISO, CDC, WHO frameworks
2. **Comprehensive**: Covers all aspects of data quality
3. **Transparent**: Every validation explained in plain English
4. **Extensible**: Easy to add disease-specific rules
5. **Auditable**: Code available for technical review
6. **Measurable**: Quality scores track improvement
7. **Educational**: Trains staff on data quality principles

---

**This positions the NCIRD Operations Center as a best-in-class data quality platform.**
