"""
Seed demo data for the NCIRD Operations Center map visualization.
Creates realistic-looking mock submissions across different states and systems.

Run this script to populate the map with demo data:
    python seed_demo_data.py
"""

import json
import os
import random
from datetime import datetime, timedelta

# Demo data configuration
DEMO_SUBMISSIONS = []

# Systems to include in demo
SYSTEMS = ['nnad', 'mumps', 'nrevss', 'iis', 'fluview', 'phlip']

# States with their "demo status" - mix of healthy, warning, and critical
# This creates a visually interesting map
STATE_SCENARIOS = {
    # Healthy states (green) - large population states doing well
    'CA': {'status': 'passed', 'submissions': 12},
    'TX': {'status': 'passed', 'submissions': 15},
    'FL': {'status': 'passed', 'submissions': 10},
    'NY': {'status': 'passed', 'submissions': 14},
    'PA': {'status': 'passed', 'submissions': 8},
    'IL': {'status': 'passed', 'submissions': 9},
    'OH': {'status': 'passed', 'submissions': 7},
    'MI': {'status': 'passed', 'submissions': 6},
    'WA': {'status': 'passed', 'submissions': 8},
    'MA': {'status': 'passed', 'submissions': 7},
    'VA': {'status': 'passed', 'submissions': 6},
    'NC': {'status': 'passed', 'submissions': 5},
    'MN': {'status': 'passed', 'submissions': 6},
    'CO': {'status': 'passed', 'submissions': 5},
    'OR': {'status': 'passed', 'submissions': 4},

    # Warning states (yellow) - some issues but submitting
    'GA': {'status': 'passed_with_warnings', 'submissions': 6},
    'AZ': {'status': 'passed_with_warnings', 'submissions': 5},
    'NJ': {'status': 'passed_with_warnings', 'submissions': 4},
    'TN': {'status': 'passed_with_warnings', 'submissions': 3},
    'IN': {'status': 'passed_with_warnings', 'submissions': 4},
    'MO': {'status': 'passed_with_warnings', 'submissions': 3},
    'WI': {'status': 'passed_with_warnings', 'submissions': 3},
    'MD': {'status': 'passed_with_warnings', 'submissions': 4},
    'SC': {'status': 'passed_with_warnings', 'submissions': 2},
    'AL': {'status': 'passed_with_warnings', 'submissions': 2},

    # Critical states (red) - validation failures
    'LA': {'status': 'failed', 'submissions': 3},
    'KY': {'status': 'failed', 'submissions': 2},
    'OK': {'status': 'failed', 'submissions': 2},
    'NV': {'status': 'failed', 'submissions': 1},
    'NM': {'status': 'failed', 'submissions': 1},
    'MS': {'status': 'failed', 'submissions': 1},
    'AR': {'status': 'failed', 'submissions': 1},

    # No data states (gray) - haven't submitted yet
    # These are intentionally omitted to show as gray on the map
}

def generate_submission_id():
    """Generate a unique submission ID"""
    return f"sub_{datetime.now().strftime('%Y%m%d')}_{random.randint(10000, 99999)}"

def generate_errors(status, system_id):
    """Generate realistic error messages based on status"""
    error_templates = {
        'nnad': [
            {'code': 'NNAD-001', 'message': 'Missing required field: condition_code', 'severity': 'error'},
            {'code': 'NNAD-002', 'message': 'Invalid date format in onset_date', 'severity': 'error'},
            {'code': 'NNAD-003', 'message': 'Case classification code not in valid set', 'severity': 'warning'},
        ],
        'mumps': [
            {'code': 'MMP-001', 'message': 'MMG version mismatch - expected 1.0.2', 'severity': 'error'},
            {'code': 'MMP-002', 'message': 'Vaccination history incomplete', 'severity': 'warning'},
        ],
        'nrevss': [
            {'code': 'NRV-001', 'message': 'Lab ID not found in registered facilities', 'severity': 'error'},
            {'code': 'NRV-002', 'message': 'Specimen count exceeds tests performed', 'severity': 'error'},
        ],
        'iis': [
            {'code': 'IIS-001', 'message': 'Invalid CVX code: 999', 'severity': 'error'},
            {'code': 'IIS-002', 'message': 'Administration date in future', 'severity': 'warning'},
        ],
        'fluview': [
            {'code': 'FLU-001', 'message': 'ILI percentage exceeds 100%', 'severity': 'error'},
            {'code': 'FLU-002', 'message': 'Week number out of range', 'severity': 'warning'},
        ],
        'phlip': [
            {'code': 'PHL-001', 'message': 'HL7 segment OBX missing required fields', 'severity': 'error'},
            {'code': 'PHL-002', 'message': 'Specimen type code deprecated', 'severity': 'warning'},
        ],
    }

    if status == 'passed':
        return []
    elif status == 'passed_with_warnings':
        # Return 1-2 warnings
        templates = [e for e in error_templates.get(system_id, []) if e['severity'] == 'warning']
        if not templates:
            templates = error_templates.get(system_id, [])[:1]
        return random.sample(templates, min(len(templates), random.randint(1, 2)))
    else:  # failed
        # Return 2-4 errors including at least one error-severity
        templates = error_templates.get(system_id, [])
        return random.sample(templates, min(len(templates), random.randint(2, 4)))

def create_submission(state, system_id, status, days_ago):
    """Create a single mock submission"""
    timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

    errors = generate_errors(status, system_id)
    error_count = len([e for e in errors if e.get('severity') == 'error'])
    warning_count = len([e for e in errors if e.get('severity') == 'warning'])

    return {
        'submission_id': generate_submission_id(),
        'system_id': system_id,
        'system_name': system_id.upper(),
        'jurisdiction': state,
        'filename': f"{state}_{system_id}_{timestamp.strftime('%Y%m%d')}.csv",
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'status': status,
        'rows_processed': random.randint(100, 5000),
        'errors': errors,
        'error_count': error_count,
        'warning_count': warning_count,
        'validation_time_ms': random.randint(500, 3000),
    }

def seed_demo_data():
    """Generate and save demo data"""
    submissions = []

    for state, config in STATE_SCENARIOS.items():
        status = config['status']
        num_submissions = config['submissions']

        # Create submissions across different systems and time periods
        for i in range(num_submissions):
            system = random.choice(SYSTEMS)
            days_ago = random.randint(0, 30)

            # Vary status slightly - not all submissions from a "warning" state fail
            if status == 'passed':
                actual_status = 'passed' if random.random() > 0.1 else 'passed_with_warnings'
            elif status == 'passed_with_warnings':
                r = random.random()
                if r > 0.6:
                    actual_status = 'passed'
                elif r > 0.2:
                    actual_status = 'passed_with_warnings'
                else:
                    actual_status = 'failed'
            else:  # failed
                actual_status = 'failed' if random.random() > 0.3 else 'passed_with_warnings'

            submission = create_submission(state, system, actual_status, days_ago)
            submissions.append(submission)

    # Sort by timestamp (most recent first)
    submissions.sort(key=lambda x: x['timestamp'], reverse=True)

    # Save to data directory
    data_dir = 'data'
    os.makedirs(data_dir, exist_ok=True)

    filepath = os.path.join(data_dir, 'submissions.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(submissions, f, indent=2)

    print(f"Created {len(submissions)} demo submissions")
    print(f"Saved to {filepath}")

    # Summary
    states_with_data = len(STATE_SCENARIOS)
    passed = sum(1 for s in submissions if s['status'] == 'passed')
    warnings = sum(1 for s in submissions if s['status'] == 'passed_with_warnings')
    failed = sum(1 for s in submissions if s['status'] == 'failed')

    print(f"\nSummary:")
    print(f"  States with data: {states_with_data}")
    print(f"  Passed: {passed}")
    print(f"  With warnings: {warnings}")
    print(f"  Failed: {failed}")

if __name__ == '__main__':
    seed_demo_data()
