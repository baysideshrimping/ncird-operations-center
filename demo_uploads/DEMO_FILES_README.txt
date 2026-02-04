NCIRD Operations Center - Demo Upload Files
============================================

These files are designed for demonstrating the data validation system.
Upload them to test the validators and see validation results in action.

PASS FOLDER (Should validate successfully)
------------------------------------------

GA_NNAD_20260201.csv
  - Georgia NNAD submission with 5 Pertussis/Measles cases
  - Uses correct SNOMED codes (410605003=Confirmed, 2931005=Probable)
  - Valid dates, jurisdictions, and demographic data

TX_Mumps_20260115.csv
  - Texas Mumps surveillance with 5 cases
  - Correct lab codes (10828004=Positive, 260385009=Negative)
  - Proper sex-specific complication coding (orchitis for male only)
  - Valid genotype codes (G)

NY_NNAD_20260128.csv
  - New York NNAD with Hepatitis A and Salmonellosis cases
  - Outbreak-associated cases included
  - All dates and codes valid

Quest_NREVSS_2026W05.csv
  - Quest Diagnostics lab data for MMWR Week 2026-W05
  - RSV, Influenza A/B across GA, TX, AZ
  - Math checks: positive + negative = total (all correct)

LabCorp_NREVSS_2026W04.csv
  - LabCorp surveillance from NC and FL
  - Includes SARS-CoV-2 and Human Metapneumovirus
  - All calculations validate correctly


FAIL FOLDER (Should trigger validation errors)
----------------------------------------------

ZZ_NNAD_20260202.csv - INVALID JURISDICTIONS
  - Rows 2,3,5: Invalid state codes "ZZ" and "XX"
  - Row 4: Invalid case_status code "INVALID_CODE"
  - Row 5: Onset date (2026-02-10) AFTER report date (2026-02-02)

CA_Mumps_BadLabCodes.csv - INVALID LAB CODES + LOGIC ERRORS
  - Rows 2,3: Text lab codes "POSITIVE"/"NEGATIVE" instead of SNOMED
  - Row 4: Parotitis=N but duration=8 days (contradiction)
  - Row 5: Parotitis duration=1 day (below 2-day clinical threshold)
  - Row 6: Orchitis=Y for female patient (anatomically impossible)
  - Row 6: Invalid genotype "Z" (valid: A-L, N, UNK)

BioReference_NREVSS_2026W06.csv - MATH AND FORMAT ERRORS
  - Row 2: positive(150) + negative(900) = 1050 ≠ total(1000)
  - Row 3: positive(250) + negative(700) = 950 ≠ total(1000)
  - Row 4: Invalid week format "2026W06" (missing hyphen)
  - Row 5: Invalid state code "ZZ"
  - Row 6: Non-standard virus type "Custom Virus Type"
  - Row 7: Negative positive_results value (-10)
  - Row 8: Percent positive 125.0% (impossible, max is 100%)

FL_NNAD_DateErrors.csv - DATE AND LOGIC ERRORS
  - Row 2: Onset (2026-01-20) AFTER report (2026-01-15)
  - Row 3: Invalid date format "January 15 2026"
  - Row 4: Invalid date format "2026/01/05" (uses slashes)
  - Row 5: Age=150 years (implausible)
  - Row 6: Male patient with pregnancy=Y (impossible)

AZ_Mumps_SexMismatch.csv - SEX-SPECIFIC COMPLICATION ERRORS
  - Row 2: Orchitis=Y for female patient (impossible)
  - Row 3: Oophoritis=Y for male patient (impossible)
  - Row 4: Severe complications (encephalitis, meningitis) but not hospitalized
  - Row 5: Parotitis duration=75 days (implausible, likely typo)
  - Row 6: Confirmed case with negative lab result (classification mismatch)


DEMO TIPS
---------
1. Start with a PASS file to show successful validation
2. Upload a FAIL file and watch the error messages appear
3. Point out how errors link to specific documentation rules
4. Show how the map updates with jurisdiction data from uploads
