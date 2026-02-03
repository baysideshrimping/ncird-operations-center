"""
Data persistence utilities for JSON storage
Handles loading and saving submissions, configuration, and system state
"""

import json
import os
from datetime import datetime

def ensure_data_directory(path):
    """Ensure directory exists"""
    os.makedirs(path, exist_ok=True)

def load_json(filepath, default=None):
    """
    Load JSON from file with error handling

    Args:
        filepath: Path to JSON file
        default: Default value if file doesn't exist

    Returns:
        Parsed JSON data or default
    """
    if default is None:
        default = {}

    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading {filepath}: {e}")

    return default

def save_json(filepath, data):
    """
    Save data to JSON file

    Args:
        filepath: Path to JSON file
        data: Data to save

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except (IOError, TypeError) as e:
        print(f"Error saving {filepath}: {e}")
        return False

def load_submissions(filepath='data/submissions.json'):
    """Load all submissions"""
    return load_json(filepath, default=[])

def save_submission(submission, filepath='data/submissions.json'):
    """
    Save a new submission to the list

    Args:
        submission: Submission dict to save
        filepath: Path to submissions file

    Returns:
        True if successful
    """
    submissions = load_submissions(filepath)

    # Add timestamp if not present
    if 'timestamp' not in submission:
        submission['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Add to beginning of list (most recent first)
    submissions.insert(0, submission)

    return save_json(filepath, submissions)

def get_submission_by_id(submission_id, filepath='data/submissions.json'):
    """Get a specific submission by ID"""
    submissions = load_submissions(filepath)
    for sub in submissions:
        if sub.get('submission_id') == submission_id:
            return sub
    return None

def get_submissions_by_system(system_id, filepath='data/submissions.json'):
    """Get all submissions for a specific system"""
    submissions = load_submissions(filepath)
    return [sub for sub in submissions if sub.get('system_id') == system_id]

def get_submissions_by_jurisdiction(jurisdiction, filepath='data/submissions.json'):
    """Get all submissions from a specific jurisdiction"""
    submissions = load_submissions(filepath)
    return [sub for sub in submissions if sub.get('jurisdiction') == jurisdiction]

def get_recent_submissions(limit=100, filepath='data/submissions.json'):
    """Get most recent N submissions"""
    submissions = load_submissions(filepath)
    return submissions[:limit]

def clear_all_submissions(filepath='data/submissions.json'):
    """Clear all submission data"""
    return save_json(filepath, [])

def get_submission_stats(system_id=None, filepath='data/submissions.json'):
    """
    Get statistics about submissions

    Args:
        system_id: Optional system ID to filter by
        filepath: Path to submissions file

    Returns:
        dict with statistics
    """
    submissions = load_submissions(filepath)

    # Filter by system if specified
    if system_id:
        submissions = [s for s in submissions if s.get('system_id') == system_id]

    if not submissions:
        return {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'passed_with_warnings': 0,
            'pass_rate': 0
        }

    # Count by status
    passed = sum(1 for s in submissions if s.get('status') == 'passed')
    failed = sum(1 for s in submissions if s.get('status') == 'failed')
    passed_with_warnings = sum(1 for s in submissions if s.get('status') == 'passed_with_warnings')

    return {
        'total': len(submissions),
        'passed': passed,
        'failed': failed,
        'passed_with_warnings': passed_with_warnings,
        'pass_rate': round((passed / len(submissions)) * 100, 1) if submissions else 0
    }

def get_system_health(system_id, filepath='data/submissions.json'):
    """
    Get health status for a system

    Args:
        system_id: System identifier
        filepath: Path to submissions file

    Returns:
        dict with health metrics
    """
    submissions = get_submissions_by_system(system_id, filepath)

    if not submissions:
        return {
            'status': 'no_data',
            'last_submission': None,
            'days_since_last': None,
            'recent_pass_rate': 0
        }

    # Most recent submission
    latest = submissions[0]
    last_date = datetime.strptime(latest.get('timestamp'), '%Y-%m-%d %H:%M:%S')
    days_since = (datetime.now() - last_date).days

    # Recent pass rate (last 10 submissions)
    recent = submissions[:10]
    passed = sum(1 for s in recent if s.get('status') == 'passed')
    recent_pass_rate = round((passed / len(recent)) * 100, 1) if recent else 0

    # Determine overall status
    if days_since <= 1:
        status = 'healthy'
    elif days_since <= 7:
        status = 'warning'
    else:
        status = 'alert'

    return {
        'status': status,
        'last_submission': latest.get('timestamp'),
        'days_since_last': days_since,
        'recent_pass_rate': recent_pass_rate,
        'total_submissions': len(submissions)
    }
