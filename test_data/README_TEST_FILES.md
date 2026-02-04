# Demo Test Files - Intentional Errors for Clickable Link Demo

These test files contain **intentional validation errors** to demonstrate the clickable error link feature that jumps to documentation.

## 📁 Files

### 1. `nnad_demo_errors.csv` (NNAD/NNDSS Case Notifications)

**Intentional Errors:**
- **Row 2**: Age = 150 years (exceeds max 120)
  - ✅ Triggers: `#nnad-accuracy-2-1` - Age Plausibility
  - Click error → Jumps to Accuracy section in documentation

- **Row 2**: Illness onset date (2026-01-25) AFTER report date (2026-01-20)
  - ✅ Triggers: `#nnad-consistency-3-1` - Date Sequence Logic
  - Click error → Jumps to Consistency section in documentation

- **Row 3**: Patient died (Y) but not hospitalized (N)
  - ✅ Triggers: `#nnad-consistency-3-2` - Hospitalization Death Logic (WARNING)
  - Click warning → Jumps to Consistency section in documentation

### 2. `mumps_demo_errors.csv` (Mumps Disease Surveillance)

**Intentional Errors:**
- **Row 1**: Lab result = "positive" (free text instead of SNOMED CT code)
  - ✅ Triggers: `#mumps-validity-4-1` - Lab Result SNOMED CT Codes
  - Click error → Jumps to Validity section showing valid codes (10828004, etc.)

- **Row 2**: Specimen collection date (2026-01-25) AFTER lab result date (2026-01-20)
  - ✅ Triggers: `#mumps-consistency-3-2` - Specimen Date Before Result
  - Click error → Jumps to Consistency section explaining temporal logic

### 3. `nrevss_demo_errors.csv` (Laboratory Surveillance)

**Intentional Errors:**
- **Row 1**: Reporting week = "Week 4" (wrong format, should be YYYY-WNN)
  - ✅ Triggers: `#nrevss-validity-4-1` - CDC Week Format
  - Click error → Jumps to Validity section showing correct format (2026-W04)

- **Row 2**: Total specimens = 150,000 (exceeds max 100,000)
  - ✅ Triggers: `#nrevss-accuracy-2-1` - Specimen Count Range
  - Click error → Jumps to Accuracy section explaining plausible ranges

- **Row 3**: Positive (30) + Negative (150) = 180, but Total = 200
  - ✅ Triggers: `#nrevss-consistency-3-1` - Positive + Negative = Total
  - Click error → Jumps to Consistency section with code drill-down

## 🎯 Demo Flow

1. **Upload** one of these files via the Submit page
2. **View validation results** - errors will be displayed
3. **Click on any error message** (blue underlined link)
4. **Automatically**:
   - Switches to correct system tab (NNAD/Mumps/NREVSS)
   - Opens the relevant accordion section
   - Scrolls to the exact validation rule
   - Highlights the rule with yellow shadow for 2 seconds
5. **Read** plain English explanation + view code drill-down
6. **Understand WHY** the validation failed

## 💡 Educational Value

These clickable links transform the platform from just a validator to an **educational tool** that:
- Explains WHY data failed validation
- Shows the exact code implementing the rule
- Links to industry standards (SNOMED CT, CDC MMWR, ISO 8601)
- Trains staff on data quality principles

Perfect for demonstrating to Kiran, Prasanthi, and Brian how the platform helps epidemiologists learn validation rules!
