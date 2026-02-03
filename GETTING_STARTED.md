# Getting Started with NCIRD Operations Center

## Quick Start

### 1. Install Dependencies
```bash
cd ncird-operations-center
pip install -r requirements.txt
```

### 2. Initialize Data Storage
```bash
mkdir -p data/submissions
echo "[]" > data/submissions.json
echo "{}" > data/config.json
```

### 3. Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## Testing with Mock Data

The `mock_data/` directory contains sample files for testing:

### NNAD (National Notifiable Diseases)
- `mock_data/nnad/nnad_sample_valid.csv` - Valid case notifications
- `mock_data/nnad/nnad_sample_errors.csv` - File with errors for testing

### Mumps Surveillance
- `mock_data/mumps/mumps_sample_valid.csv` - Valid mumps cases
- `mock_data/mumps/mumps_sample_errors.csv` - File with validation errors

### NREVSS (Laboratory Data)
- `mock_data/nrevss/nrevss_sample_valid.csv` - Valid lab reports
- `mock_data/nrevss/nrevss_sample_errors.csv` - File with errors

## Demo Walkthrough

### For Your NCIRD Demo:

1. **Start with the Dashboard**
   - Navigate to `http://localhost:5000`
   - Show the operations center with all 14+ data streams
   - Highlight the different categories (Disease Surveillance, Lab Surveillance, etc.)

2. **Demonstrate NNAD Validation**
   - Click on "NNAD (NNDSS)" system
   - Click "Submit Data"
   - Upload `mock_data/nnad/nnad_sample_valid.csv` → Shows PASSED
   - Upload `mock_data/nnad/nnad_sample_errors.csv` → Shows FAILED with specific errors
   - Point out: Invalid jurisdiction, bad date formats, missing required fields

3. **Demonstrate Mumps Validation**
   - Navigate to Mumps system
   - Upload `mock_data/mumps/mumps_sample_valid.csv`
   - Show disease-specific validation (parotitis, lab results, MMG compliance)
   - Upload error file to demonstrate mumps-specific validation

4. **Demonstrate NREVSS (Lab Data)**
   - Navigate to NREVSS system
   - Upload `mock_data/nrevss/nrevss_sample_valid.csv`
   - Show lab data validation (specimens, virus types, positivity rates)
   - Demonstrate math validation (positive + negative = total)

5. **Show the Map View**
   - Click "Map" in navigation
   - Show geographic distribution of submissions
   - Explain how this provides jurisdiction-level oversight

6. **Highlight Key Features**
   - **Modular Design**: Each system has its own validator module
   - **Extensibility**: Adding new systems is straightforward
   - **Validation Depth**: System-specific rules (Generic MMG for NNAD, Mumps MMG v1.0.2, etc.)
   - **User-Friendly Errors**: Detailed, actionable error messages
   - **Cross-System Analytics**: Dashboard shows health across all systems

## Key Talking Points

### Architecture
- **Base Validator Pattern**: All validators inherit from BaseValidator
- **Config-Driven**: Data streams defined in config.py
- **API-First**: RESTful API for programmatic access
- **Deployment Ready**: Configured for Render.com deployment

### Scalability
- Easy to add new data streams (create validator, add to config)
- Handles different data formats (CSV, HL7, JSON, Excel)
- Modular validation rules
- Can scale to all 23 NCIRD-managed diseases

### Value Proposition
- **Single Platform**: Unified view of all NCIRD data streams
- **Early Error Detection**: Catch quality issues before CDC submission
- **Time Savings**: Automated validation vs. manual review
- **Visibility**: Real-time dashboard for surveillance coordinators
- **Quality Improvement**: Track trends, identify systemic issues

## Admin Functions

### Clear All Data
Navigate to `/admin` and use password `ncird2026` to clear all submissions

## Configuration

Edit `config.py` to:
- Enable/disable data streams
- Add new systems
- Configure validation thresholds
- Set alert rules

## API Endpoints

- `GET /api/systems` - List all data streams
- `GET /api/submissions` - All submissions
- `GET /api/submissions/<system_id>` - System-specific submissions
- `GET /api/system-status` - Health status for all systems
- `GET /api/jurisdictions/<state_abbr>` - State-specific data
- `POST /api/submit/<system_id>` - Programmatic submission
- `POST /api/clear-data` - Clear all data (password protected)

## Deployment

The application is configured for Render.com deployment via `render.yaml`.

For local development:
```bash
python app.py
```

For production:
```bash
gunicorn app:app
```

## Support

For questions about the demo, contact Kevin at Peraton/NCIRD.

## Next Steps After Demo

Based on feedback from Kiran, Prasanthi, Brian, and Anjana:

1. Prioritize which data streams to implement first
2. Understand current validation workflows for Mumps/NNAD
3. Discuss integration with existing NCIRD infrastructure
4. Plan pilot deployment with select data streams
5. Gather requirements for additional features
