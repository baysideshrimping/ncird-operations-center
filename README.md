# NCIRD Data Operations Center

A unified platform for monitoring, validating, and visualizing all National Center for Immunization and Respiratory Diseases (NCIRD) data streams.

## Built for Modularity and Enterprise Deployment

This application was designed from the ground up with two key principles:

1. **Modular Architecture** - Each data stream has its own validation module that inherits from a common `BaseValidator` class. Adding a new CDC data system requires only creating a new validator file and registering it in config—the dashboard automatically picks it up. This makes it easy to expand coverage as NCIRD's data landscape evolves.

2. **Databricks-Ready** - The codebase uses environment-based configuration (`os.environ.get()`) for all paths and secrets, making it portable between local development, cloud platforms like Render.com, and enterprise Databricks environments on CDC/HHS infrastructure. Data persistence paths, upload folders, and credentials are all configurable for `/dbfs/` storage.

## Recent Updates

- **Interactive Geographic Map** - D3.js SVG map with color-coded states showing submission status (healthy/warning/critical), hover tooltips, and filterable jurisdiction grid
- **Auto-jurisdiction Detection** - Uploads automatically appear on the map by extracting state codes from data fields (`reporting_jurisdiction`, `state`) or filenames
- **Templates & Data Dictionaries** - Downloadable CSV templates and field specifications for all data streams
- **Standards & References** - Links to official CDC Message Mapping Guides (MMGs) and documentation
- **Clickable Validation Documentation** - 62 of 67 validation rules (93%) now link directly to source code with line-by-line explanations
- **Expanded Validation Coverage** - 40+ new validation rules based on CDC/HHS data quality research

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

### Option 1: Render.com (Cloud Platform)

Configured for Render.com deployment:
```bash
git push  # Automatic deployment via render.yaml
```

### Option 2: Databricks (CDC/HHS Enterprise Environment)

For deployment on Peraton CDC/HHS machines using Databricks clusters.

#### Prerequisites
- Databricks workspace access (Azure or AWS)
- Python 3.11+ runtime
- Cluster with public IP enabled

#### Quick Start

**1. Create a Cluster**
```
Runtime: Spark 13.3 LTS (Python 3.11)
Driver/Worker Nodes: 2x Standard_DS3_v2
Enable: Public IP for driver node
```

**2. Install Dependencies**

In a Databricks notebook cell:
```python
%sh
pip install -r requirements.txt
```

**3. Mount Your Repository**

**Option A - Databricks Repos (Recommended)**
- Navigate to: Repos → Create Repo
- Paste GitHub URL: `https://github.com/<your-org>/ncird-operations-center`
- Checkout main branch
- Path: `/Workspace/Repos/<user>/ncird-operations-center`

**Option B - Git Clone to DBFS**
```python
%sh
git clone https://github.com/<your-org>/ncird-operations-center /dbfs/tmp/ncird
```

**4. Configure Data Persistence**

Point data storage to DBFS for persistence across cluster restarts:
```python
import os
# Set data directory to DBFS (persists across restarts)
os.environ["DATA_DIR"] = "/dbfs/FileStore/ncird/data"
os.environ["UPLOAD_FOLDER"] = "/dbfs/FileStore/ncird/uploads"
```

**5. Start the Application**

Create a notebook cell:
```python
import os
from app import app

# Configure for Databricks
os.environ["DATA_DIR"] = "/dbfs/FileStore/ncird/data"
os.environ["UPLOAD_FOLDER"] = "/dbfs/FileStore/ncird/uploads"

# Create directories if they don't exist
os.makedirs(os.environ["DATA_DIR"], exist_ok=True)
os.makedirs(os.environ["UPLOAD_FOLDER"], exist_ok=True)

# Run with Gunicorn
os.system("gunicorn app:app --bind 0.0.0.0:8050 --timeout 120")
```

**6. Access the Application**

Application will be available at:
```
https://<cluster-id>.azuredatabricks.net:8050
```

Or create a Databricks Job to expose as an HTTP endpoint.

#### Databricks Jobs Deployment

For production deployment, create a Databricks Job:

1. **Create Job**
   - Name: "NCIRD Operations Center"
   - Type: Python Script
   - Script: `/Workspace/Repos/<user>/ncird-operations-center/app.py`

2. **Job Configuration**
   ```json
   {
     "name": "NCIRD-Ops-Center",
     "tasks": [{
       "task_key": "run_app",
       "python_wheel_task": {
         "package_name": "ncird-operations-center",
         "entry_point": "app"
       },
       "libraries": [{
         "requirements": "/Workspace/Repos/<user>/ncird-operations-center/requirements.txt"
       }]
     }],
     "job_clusters": [{
       "job_cluster_key": "ncird_cluster",
       "new_cluster": {
         "spark_version": "13.3.x-scala2.12",
         "node_type_id": "Standard_DS3_v2",
         "num_workers": 2
       }
     }]
   }
   ```

3. **Environment Variables**
   - `DATA_DIR`: `/dbfs/FileStore/ncird/data`
   - `UPLOAD_FOLDER`: `/dbfs/FileStore/ncird/uploads`
   - `SECRET_KEY`: (Set in Databricks Secrets)
   - `ADMIN_PASSWORD`: (Set in Databricks Secrets)

#### Data Persistence on Databricks

| Location | Persistence | Use Case |
|----------|-------------|----------|
| `/tmp/` | ❌ Not persistent | Temporary files only |
| `/dbfs/FileStore/` | ✅ Persistent | Submission data, uploads |
| `/Workspace/Repos/` | ✅ Git-backed | Application code |

**Important:** Always use `/dbfs/FileStore/` for data storage to ensure submissions persist across cluster restarts.

#### Security Considerations

- Store secrets in **Databricks Secrets** (not environment variables)
- Enable cluster access controls
- Use service principals for automated jobs
- Restrict network access to CDC/HHS networks only

#### Monitoring & Logs

View application logs:
```python
%sh
tail -f /databricks/driver/logs/stderr
```

Or use Databricks Jobs UI to monitor job runs and view logs.

#### Cleanup

When testing is complete:
```bash
# Stop cluster to avoid charges
# Delete job if no longer needed
# DBFS data persists - delete manually if needed
```

#### Troubleshooting

**Issue: App not accessible**
- Verify cluster has public IP enabled
- Check security group allows inbound on port 8050
- Confirm Gunicorn is binding to 0.0.0.0 (not 127.0.0.1)

**Issue: Data not persisting**
- Verify using `/dbfs/FileStore/` (not `/tmp/`)
- Check DBFS write permissions
- Confirm directories created with correct paths

**Issue: Dependencies missing**
- Re-run `pip install -r requirements.txt`
- Restart Python kernel
- Check cluster Python version matches requirements (3.11+)

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
