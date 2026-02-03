# NCIRD Data Operations Center

A unified platform for monitoring, validating, and visualizing all National Center for Immunization and Respiratory Diseases (NCIRD) data streams.

## Overview

The NCIRD Data Operations Center provides real-time visibility into the health and status of 14+ CDC data surveillance systems, including:

- **NNAD (NNDSS)** - National Notifiable Diseases Surveillance System
- **Mumps** - Mumps-specific disease surveillance
- **DST NREVSS** - Respiratory and Enteric Virus Surveillance
- **NIS** - National Immunization Survey
- **IIS** - Immunization Information Systems
- **VSD** - Vaccine Safety Datalink
- **VaxView** - Vaccination Coverage Visualization
- **CMS** - Medicare/Medicaid Claims Data
- **KABB Omnibus** - Knowledge, Attitudes, Beliefs, Behaviors Surveys
- **PHLIP** - Public Health Laboratory Interoperability
- **IQVIA** - Commercial Healthcare Data
- **FluView** - Influenza Surveillance
- **eClearance** - CDC Clearance Workflow
- **RI/RRVR** - Respiratory Illness Surveillance

## Key Features

### 1. Unified Dashboard
- Real-time status of all data streams
- At-a-glance health indicators
- System-wide alerts and notifications

### 2. Data Validation
- Modular validation engines for each data stream
- Automated quality checks
- Detailed error reporting with remediation guidance

### 3. Geographic Visualization
- Interactive US map showing submission status by jurisdiction
- Multi-system overlay capability
- State-by-state drill-down

### 4. Submission Tracking
- Historical submission records
- Timeliness metrics
- Completeness and quality trends

### 5. Cross-System Analytics
- Compare performance across data streams
- Identify systemic issues
- Track improvements over time

## Architecture

### Modular Design
Each data stream has its own validation module that inherits from a common `BaseValidator` class, ensuring consistency while allowing system-specific rules.

```
validators/
├── base_validator.py          # Abstract base class
├── nnad_validator.py          # Disease surveillance
├── mumps_validator.py         # Mumps MMG
├── nrevss_validator.py        # Lab data
└── ...                        # Additional systems
```

### Data Models
- `Submission` - Tracks file uploads and validation runs
- `ValidationResult` - Stores validation outcomes and errors
- `DataStream` - Metadata about each surveillance system
- `Jurisdiction` - State/territory information

### Extensibility
Adding a new data stream requires:
1. Create validator in `validators/` directory
2. Define validation rules specific to that system
3. Register in `config.py`
4. System automatically appears in dashboard

## Installation

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
pip install -r requirements.txt
python app.py
```

Access at: `http://localhost:5000`

## Usage

### Upload Data
1. Navigate to specific system (e.g., /submit/nnad)
2. Upload CSV or HL7 file
3. System auto-detects format and runs validation
4. View results in dashboard

### Monitor Systems
1. Access main dashboard at `/`
2. View status of all systems
3. Click any system for detailed view
4. Click any state on map for jurisdiction-specific data

### API Access
Programmatic access available:
- `GET /api/systems` - List all data streams
- `GET /api/submissions` - All submissions
- `GET /api/submissions/<system_id>` - System-specific submissions
- `GET /api/jurisdictions/<state_abbr>` - State-specific data
- `POST /api/submit/<system_id>` - Submit data

## Configuration

Edit `config.py` to:
- Add/remove data streams
- Configure validation thresholds
- Set alert rules
- Customize dashboard layout

## Data Streams

Each system has specific requirements documented in its validator module. See validator source code for detailed validation rules.

## Development

### Adding a New Validator
```python
from validators.base_validator import BaseValidator

class MySystemValidator(BaseValidator):
    def __init__(self):
        super().__init__(
            system_id="my_system",
            system_name="My System Name",
            description="What this system does"
        )

    def validate_structure(self, df):
        # Implement structure validation
        pass

    def validate_content(self, df):
        # Implement content validation
        pass
```

### Running Tests
```bash
pytest tests/
```

## Deployment

Configured for Render.com deployment:
```bash
git push  # Automatic deployment via render.yaml
```

## Project Structure

```
ncird-operations-center/
├── app.py                      # Main Flask application
├── config.py                   # Configuration
├── requirements.txt            # Dependencies
├── validators/                 # Validation modules
├── models/                     # Data models
├── utils/                      # Shared utilities
├── templates/                  # HTML templates
├── static/                     # CSS, JS, assets
├── data/                       # Runtime data storage
├── mock_data/                  # Test datasets
└── tests/                      # Unit tests
```

## License

CDC Public Domain

## Contact

For questions or support, contact: NCIRD Data Team

## Acknowledgments

Built by Kevin for NCIRD/Peraton demonstration.
Extends patterns from BRFSS Dashboard and PRISM Validator projects.
