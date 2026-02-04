# Test Files for NCIRD Operations Center Demo

This directory contains test files for demonstrating the validation system and clickable error links.

## 📂 File Organization

### ✅ Valid Sample Files (Pass Validation)
Use these to demonstrate **successful validation** and clean data submission:

- **`nnad_valid_sample.csv`** - Clean NNAD case notifications (all validations pass)
- **`mumps_valid_sample.csv`** - Valid mumps surveillance data
- **`nrevss_valid_sample.csv`** - Valid laboratory surveillance data

### ❌ Demo Error Files (Intentional Errors)
Use these to demonstrate **clickable error links** that jump to documentation:

- **`nnad_demo_errors.csv`** - NNAD with validation errors
- **`mumps_demo_errors.csv`** - Mumps with validation errors
- **`nrevss_demo_errors.csv`** - NREVSS with validation errors

---

## 🎯 Demo Flow

### Part 1: Show Successful Validation
1. Upload `nnad_valid_sample.csv`
2. Show **✅ Passed** status with 0 errors
3. Demonstrate clean data acceptance

### Part 2: Show Error Detection + Clickable Links
1. Upload `nnad_demo_errors.csv`
2. Point out **clickable blue error messages**
3. Click an error → Watch it jump to documentation
4. Show code drill-down feature

---

## 📋 Detailed Error Breakdown

### NNAD Demo Errors (`nnad_demo_errors.csv`)

| Row | Error | Triggers Doc Link | Demonstrates |
|-----|-------|-------------------|--------------|
| 2 | Age = 150 years | `#nnad-accuracy-2-1` | Age plausibility validation |
| 2 | Onset (2026-01-25) after Report (2026-01-20) | `#nnad-consistency-3-1` | Date sequence logic |
| 3 | Died=Y but Hospitalized=N | `#nnad-consistency-3-2` | Clinical logic consistency |

**Click any error** → Auto-switches to NNAD tab → Opens Accuracy/Consistency section → Highlights rule

### Mumps Demo Errors (`mumps_demo_errors.csv`)

| Row | Error | Triggers Doc Link | Demonstrates |
|-----|-------|-------------------|--------------|
| 1 | Lab result = "positive" (free text) | `#mumps-validity-4-1` | SNOMED CT code requirement |
| 2 | Specimen date (2026-01-25) after result (2026-01-20) | `#mumps-consistency-3-2` | Temporal validation |

**Click error** → Shows valid SNOMED codes → Code drill-down available

### NREVSS Demo Errors (`nrevss_demo_errors.csv`)

| Row | Error | Triggers Doc Link | Demonstrates |
|-----|-------|-------------------|--------------|
| 1 | Week = "Week 4" (wrong format) | `#nrevss-validity-4-1` | CDC MMWR week format (YYYY-WNN) |
| 2 | Total = 150,000 (exceeds max) | `#nrevss-accuracy-2-1` | Specimen count plausibility |
| 3 | Positive (30) + Negative (150) ≠ Total (200) | `#nrevss-consistency-3-1` | Sum validation logic |

**Click error** → See format examples → View code implementation

---

## 💡 Key Demo Points

### For Kiran, Prasanthi, and Brian (NCIRD Developers):

1. **Educational Tool**: Not just validation, but **training** for jurisdictions
2. **Transparent**: Click error → See WHY it failed + exact code
3. **Standards-Based**: Links to CDC MVPS, CSTE, ISO 8000 frameworks
4. **40+ New Validations**: Comprehensive coverage based on CDC research
5. **Practical**: Catches real submission errors (typos, format issues, logic errors)

### Demo Script:

> "Let me show you a submission with errors..."
>
> *[Upload mumps_demo_errors.csv]*
>
> "See this error: 'Invalid lab result code: positive'?"
>
> *[Click the blue link]*
>
> "It **automatically jumps** to the exact validation rule, shows you the valid SNOMED CT codes, explains WHY it failed, and even lets you drill down to see the actual validation code."
>
> "Now when a state submits data with errors, they can **learn** what went wrong instead of just getting rejected."

---

## 🔄 Testing Workflow

### Quick Test:
```bash
1. Start server: python app.py
2. Open: http://localhost:5000
3. Upload: test_data/mumps_demo_errors.csv
4. Click any error link
5. Verify: Jumps to documentation, highlights rule
```

### Full Demo Sequence:
1. **Dashboard** → Show all 3 data streams
2. **Valid file** → Upload `nnad_valid_sample.csv` → Show success
3. **Error file** → Upload `mumps_demo_errors.csv` → Show clickable errors
4. **Documentation** → Click error → Jump to exact rule
5. **Code drill-down** → Show "Show Code" button

---

## 📊 Total Validation Coverage

- **NNAD**: 30+ validations (19 new + 11 original)
- **Mumps**: 25+ validations (20 new + 5 original)
- **NREVSS**: 12+ validations (6 new + 6 original)

**All with clickable documentation links!**
