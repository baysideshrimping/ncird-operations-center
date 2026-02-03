"""
Configuration for NCIRD Data Operations Center
Defines all data streams, validation settings, and system parameters
"""

import os

# Flask configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'ncird-ops-center-dev-key-2026')
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
UPLOAD_FOLDER = 'data/submissions'

# Data persistence
DATA_DIR = 'data'
SUBMISSIONS_FILE = os.path.join(DATA_DIR, 'submissions.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

# Admin password for data management
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'ncird2026')

# NCIRD Data Streams Configuration
# Each data stream has metadata and validation settings
DATA_STREAMS = {
    'nnad': {
        'id': 'nnad',
        'name': 'NNAD (NNDSS)',
        'full_name': 'National Notifiable Diseases Surveillance System',
        'description': 'State health departments submit case notifications for 120+ notifiable diseases',
        'category': 'Disease Surveillance',
        'data_type': 'Case-based',
        'format': ['HL7', 'CSV'],
        'frequency': 'Ongoing',
        'jurisdictions': 'all',  # All 50 states + 6 territories
        'validator': 'nnad_validator',
        'enabled': True,
        'priority': 1,
        'contact': 'nndss@cdc.gov',
        'documentation': 'https://ndc.services.cdc.gov/message-mapping-guides/',
        'expected_submission_frequency': 'weekly',
        'alert_if_missing_days': 10
    },
    'mumps': {
        'id': 'mumps',
        'name': 'Mumps',
        'full_name': 'Mumps Disease Surveillance',
        'description': 'Mumps case surveillance using MMG v1.0.2 standards',
        'category': 'Disease Surveillance',
        'data_type': 'Case-based',
        'format': ['HL7', 'CSV'],
        'frequency': 'Ongoing',
        'jurisdictions': 'all',
        'validator': 'mumps_validator',
        'enabled': True,
        'priority': 1,
        'contact': 'mumps@cdc.gov',
        'documentation': 'https://ndc.services.cdc.gov/mmgpage/mumps-message-mapping-guide/',
        'expected_submission_frequency': 'weekly',
        'alert_if_missing_days': 14
    },
    'nrevss': {
        'id': 'nrevss',
        'name': 'DST NREVSS',
        'full_name': 'National Respiratory and Enteric Virus Surveillance System',
        'description': 'Laboratory-based surveillance for respiratory viruses (RSV, flu, etc.)',
        'category': 'Laboratory Surveillance',
        'data_type': 'Aggregate',
        'format': ['CSV', 'Excel'],
        'frequency': 'Weekly',
        'jurisdictions': 'labs',  # Participating laboratories
        'validator': 'nrevss_validator',
        'enabled': True,
        'priority': 1,
        'contact': 'nrevss@cdc.gov',
        'documentation': 'https://www.cdc.gov/surveillance/nrevss/',
        'expected_submission_frequency': 'weekly',
        'alert_if_missing_days': 7
    },
    'nis': {
        'id': 'nis',
        'name': 'NIS',
        'full_name': 'National Immunization Survey',
        'description': 'Phone surveys with provider verification for vaccination coverage',
        'category': 'Survey',
        'data_type': 'Survey responses',
        'format': ['CSV', 'SAS'],
        'frequency': 'Continuous',
        'jurisdictions': 'national',
        'validator': 'nis_validator',
        'enabled': True,
        'priority': 2,
        'contact': 'nis@cdc.gov',
        'documentation': 'https://www.cdc.gov/nis/',
        'expected_submission_frequency': 'quarterly',
        'alert_if_missing_days': 100
    },
    'iis': {
        'id': 'iis',
        'name': 'IIS',
        'full_name': 'Immunization Information Systems',
        'description': 'State/local immunization registries with data exchange via IZ Gateway',
        'category': 'Registry',
        'data_type': 'HL7 messages',
        'format': ['HL7'],
        'frequency': 'Real-time',
        'jurisdictions': 'all',  # 64 registries
        'validator': 'iis_validator',
        'enabled': True,
        'priority': 1,
        'contact': 'iisinfo@cdc.gov',
        'documentation': 'https://www.cdc.gov/iis/',
        'expected_submission_frequency': 'daily',
        'alert_if_missing_days': 3
    },
    'vsd': {
        'id': 'vsd',
        'name': 'VSD',
        'full_name': 'Vaccine Safety Datalink',
        'description': 'Monitors adverse events from 12M people in participating health systems',
        'category': 'Safety Monitoring',
        'data_type': 'Cohort data',
        'format': ['Secure data transfer'],
        'frequency': 'Ongoing',
        'jurisdictions': 'participating_sites',
        'validator': 'vsd_validator',
        'enabled': False,  # Special access required
        'priority': 1,
        'contact': 'vsd@cdc.gov',
        'documentation': 'https://www.cdc.gov/vaccinesafety/ensuringsafety/monitoring/vsd/',
        'expected_submission_frequency': 'weekly',
        'alert_if_missing_days': 10
    },
    'vaxview': {
        'id': 'vaxview',
        'name': 'VaxView',
        'full_name': 'Vaccination Coverage Visualization',
        'description': 'Public-facing dashboards showing vaccination coverage data',
        'category': 'Visualization',
        'data_type': 'Aggregated statistics',
        'format': ['JSON', 'CSV'],
        'frequency': 'Monthly',
        'jurisdictions': 'all',
        'validator': 'vaxview_validator',
        'enabled': True,
        'priority': 3,
        'contact': 'vaxview@cdc.gov',
        'documentation': 'https://www.cdc.gov/vaccines/vaxview/',
        'expected_submission_frequency': 'monthly',
        'alert_if_missing_days': 35
    },
    'cms': {
        'id': 'cms',
        'name': 'CMS',
        'full_name': 'Medicare/Medicaid Claims Data',
        'description': 'Vaccination claims data from CMS for seniors 65+',
        'category': 'Administrative Data',
        'data_type': 'Claims records',
        'format': ['CSV', 'SAS'],
        'frequency': 'Monthly',
        'jurisdictions': 'national',
        'validator': 'cms_validator',
        'enabled': False,  # Requires special data use agreement
        'priority': 2,
        'contact': 'cms-liaison@cdc.gov',
        'documentation': 'https://www.cms.gov/data',
        'expected_submission_frequency': 'monthly',
        'alert_if_missing_days': 40
    },
    'kabb': {
        'id': 'kabb',
        'name': 'KABB Omnibus',
        'full_name': 'Knowledge, Attitudes, Beliefs, Behaviors Surveys',
        'description': 'Monthly rapid surveys on vaccine knowledge, attitudes, and behaviors',
        'category': 'Survey',
        'data_type': 'Survey responses',
        'format': ['CSV', 'SPSS'],
        'frequency': 'Monthly',
        'jurisdictions': 'national',
        'validator': 'kabb_validator',
        'enabled': True,
        'priority': 2,
        'contact': 'omnibus@cdc.gov',
        'documentation': 'https://stacks.cdc.gov/view/cdc/158732',
        'expected_submission_frequency': 'monthly',
        'alert_if_missing_days': 35
    },
    'phlip': {
        'id': 'phlip',
        'name': 'PHLIP',
        'full_name': 'Public Health Laboratory Interoperability Project',
        'description': 'HL7 lab messages for influenza and other respiratory diseases',
        'category': 'Laboratory Surveillance',
        'data_type': 'HL7 messages',
        'format': ['HL7'],
        'frequency': 'Ongoing',
        'jurisdictions': 'state_labs',
        'validator': 'phlip_validator',
        'enabled': True,
        'priority': 2,
        'contact': 'phlip@cdc.gov',
        'documentation': 'https://www.aphl.org/programs/informatics/',
        'expected_submission_frequency': 'daily',
        'alert_if_missing_days': 7
    },
    'iqvia': {
        'id': 'iqvia',
        'name': 'IQVIA',
        'full_name': 'IQVIA Commercial Healthcare Data',
        'description': 'Purchased commercial healthcare analytics data',
        'category': 'Commercial Data',
        'data_type': 'Proprietary',
        'format': ['Vendor-specific'],
        'frequency': 'Monthly',
        'jurisdictions': 'national',
        'validator': None,  # External vendor
        'enabled': False,
        'priority': 3,
        'contact': 'iqvia-liaison@cdc.gov',
        'documentation': 'Internal only',
        'expected_submission_frequency': 'monthly',
        'alert_if_missing_days': 40
    },
    'fluview': {
        'id': 'fluview',
        'name': 'FluView',
        'full_name': 'Influenza Surveillance Dashboard',
        'description': 'Weekly flu surveillance reports and interactive visualizations',
        'category': 'Visualization',
        'data_type': 'Aggregated statistics',
        'format': ['JSON', 'CSV'],
        'frequency': 'Weekly',
        'jurisdictions': 'all',
        'validator': 'fluview_validator',
        'enabled': True,
        'priority': 1,
        'contact': 'fluview@cdc.gov',
        'documentation': 'https://www.cdc.gov/fluview/',
        'expected_submission_frequency': 'weekly',
        'alert_if_missing_days': 10
    },
    'eclearance': {
        'id': 'eclearance',
        'name': 'eClearance',
        'full_name': 'CDC Electronic Clearance System',
        'description': 'Internal workflow for publication and data release approvals',
        'category': 'Workflow',
        'data_type': 'Metadata',
        'format': ['Internal system'],
        'frequency': 'Ongoing',
        'jurisdictions': 'internal',
        'validator': None,  # Internal workflow system
        'enabled': False,
        'priority': 3,
        'contact': 'clearance@cdc.gov',
        'documentation': 'Internal only',
        'expected_submission_frequency': None,
        'alert_if_missing_days': None
    },
    'rrvr': {
        'id': 'rrvr',
        'name': 'RI/RRVR',
        'full_name': 'Respiratory Illness / Rhinovirus-Enterovirus Surveillance',
        'description': 'Respiratory illness surveillance and laboratory data',
        'category': 'Disease Surveillance',
        'data_type': 'Lab and clinical',
        'format': ['CSV', 'HL7'],
        'frequency': 'Weekly',
        'jurisdictions': 'all',
        'validator': 'rrvr_validator',
        'enabled': True,
        'priority': 2,
        'contact': 'respiratory@cdc.gov',
        'documentation': 'https://www.cdc.gov/surveillance/',
        'expected_submission_frequency': 'weekly',
        'alert_if_missing_days': 10
    }
}

# Categories for grouping systems
CATEGORIES = [
    'Disease Surveillance',
    'Laboratory Surveillance',
    'Survey',
    'Registry',
    'Safety Monitoring',
    'Visualization',
    'Administrative Data',
    'Commercial Data',
    'Workflow'
]

# Validation severity levels
SEVERITY_LEVELS = {
    'error': {'label': 'Error', 'color': '#dc3545', 'icon': '❌'},
    'warning': {'label': 'Warning', 'color': '#ffc107', 'icon': '⚠️'},
    'info': {'label': 'Info', 'color': '#17a2b8', 'icon': 'ℹ️'}
}

# Status indicators
STATUS_CONFIG = {
    'passed': {'label': 'Passed', 'color': '#28a745', 'icon': '✅'},
    'passed_with_warnings': {'label': 'Passed with Warnings', 'color': '#ffc107', 'icon': '⚠️'},
    'failed': {'label': 'Failed', 'color': '#dc3545', 'icon': '❌'},
    'pending': {'label': 'Pending', 'color': '#6c757d', 'icon': '⏳'},
    'no_data': {'label': 'No Data', 'color': '#e9ecef', 'icon': '—'}
}

# Get enabled data streams
def get_enabled_streams():
    """Return only enabled data streams"""
    return {k: v for k, v in DATA_STREAMS.items() if v.get('enabled', False)}

# Get streams by category
def get_streams_by_category(category):
    """Return all streams in a specific category"""
    return {k: v for k, v in DATA_STREAMS.items() if v.get('category') == category}

# Get priority streams
def get_priority_streams(min_priority=1):
    """Return streams with priority <= min_priority (1 is highest)"""
    return {k: v for k, v in DATA_STREAMS.items()
            if v.get('enabled', False) and v.get('priority', 99) <= min_priority}
