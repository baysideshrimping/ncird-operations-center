"""
NCIRD Data Operations Center
Main Flask Application

Unified platform for monitoring and validating all NCIRD data streams
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

# Import configuration
import config

# Import models
from models import ValidationResult, DataStream, Jurisdiction

# Import validators
from validators import get_validator, VALIDATOR_REGISTRY

# Import utilities
from utils.persistence import (
    load_submissions,
    save_submission,
    get_submission_by_id,
    get_submissions_by_system,
    get_submissions_by_jurisdiction,
    get_submission_stats,
    get_system_health,
    clear_all_submissions
)
from utils.state_codes import get_all_jurisdictions

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

# Ensure data directories exist
os.makedirs(config.DATA_DIR, exist_ok=True)
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

@app.route('/')
def index():
    """Main operations center dashboard"""
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    """Operations center dashboard showing all systems"""

    # Get all enabled data streams
    streams = DataStream.get_enabled_streams()

    # Get system health for each stream
    system_status = {}
    for stream in streams:
        health = get_system_health(stream.id)
        stats = get_submission_stats(stream.id)

        system_status[stream.id] = {
            'stream': stream.to_dict(),
            'health': health,
            'stats': stats
        }

    # Get recent submissions across all systems
    recent_submissions = load_submissions()[:20]

    # Calculate overall statistics
    all_stats = get_submission_stats()

    return render_template(
        'dashboard.html',
        system_status=system_status,
        recent_submissions=recent_submissions,
        overall_stats=all_stats,
        categories=config.CATEGORIES
    )


# ============================================================================
# SYSTEM-SPECIFIC VIEWS
# ============================================================================

@app.route('/system/<system_id>')
def system_detail(system_id):
    """Detailed view for a specific data stream"""

    stream = DataStream(system_id)

    if not stream.enabled:
        flash(f"System {system_id} is not enabled", 'warning')
        return redirect(url_for('dashboard'))

    # Get submissions for this system
    submissions = get_submissions_by_system(system_id)

    # Get statistics
    stats = get_submission_stats(system_id)
    health = get_system_health(system_id)

    # Get jurisdictions that have submitted
    jurisdictions = set()
    for sub in submissions:
        if sub.get('jurisdiction'):
            jurisdictions.add(sub['jurisdiction'])

    return render_template(
        'system_detail.html',
        stream=stream.to_dict(),
        submissions=submissions[:100],  # Last 100
        stats=stats,
        health=health,
        jurisdictions=sorted(jurisdictions)
    )


# ============================================================================
# FILE UPLOAD AND VALIDATION
# ============================================================================

@app.route('/submit/<system_id>', methods=['GET', 'POST'])
def submit_file(system_id):
    """File upload for a specific system"""

    stream = DataStream(system_id)

    if not stream.enabled:
        flash(f"System {system_id} is not enabled for submissions", 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # Check if file present
        if 'file' not in request.files:
            flash('No file uploaded', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)

        if file:
            # Secure filename
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{system_id}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Save file
            file.save(filepath)

            # Get validator
            validator = get_validator(system_id)

            if not validator:
                flash(f"No validator configured for {system_id}", 'error')
                return redirect(url_for('system_detail', system_id=system_id))

            # Run validation
            try:
                validation_result = validator.validate_file(filepath, filename)

                # Save submission
                save_submission(validation_result.to_dict())

                # Redirect to results
                return redirect(url_for('validation_detail',
                                        submission_id=validation_result.submission_id))

            except Exception as e:
                flash(f"Validation error: {str(e)}", 'error')
                return redirect(request.url)

    return render_template('submit.html', stream=stream.to_dict())


# ============================================================================
# VALIDATION RESULTS
# ============================================================================

@app.route('/validation/<submission_id>')
def validation_detail(submission_id):
    """Detailed validation results for a submission"""

    submission = get_submission_by_id(submission_id)

    if not submission:
        flash('Submission not found', 'error')
        return redirect(url_for('dashboard'))

    # Get system info
    stream = DataStream(submission['system_id'])

    return render_template(
        'validation_detail.html',
        submission=submission,
        stream=stream.to_dict()
    )


# ============================================================================
# GEOGRAPHIC MAP VIEW
# ============================================================================

@app.route('/map')
def map_view():
    """Interactive US map showing submission status by jurisdiction"""

    # Get all jurisdictions
    all_jurisdictions = get_all_jurisdictions()

    # Get submission status for each jurisdiction
    jurisdiction_status = {}

    for jurisdiction in all_jurisdictions:
        abbr = jurisdiction['abbr']
        submissions = get_submissions_by_jurisdiction(abbr)

        if submissions:
            # Get most recent submission
            latest = submissions[0]
            status = latest.get('status', 'no_data')

            # Count by status
            stats = {
                'total': len(submissions),
                'passed': sum(1 for s in submissions if s.get('status') == 'passed'),
                'failed': sum(1 for s in submissions if s.get('status') == 'failed'),
                'last_submission': latest.get('timestamp')
            }

            jurisdiction_status[abbr] = {
                'status': status,
                'stats': stats
            }
        else:
            jurisdiction_status[abbr] = {
                'status': 'no_data',
                'stats': None
            }

    return render_template(
        'map.html',
        jurisdictions=all_jurisdictions,
        jurisdiction_status=jurisdiction_status
    )


# ============================================================================
# VALIDATION DOCUMENTATION
# ============================================================================

@app.route('/documentation')
def documentation():
    """Validation documentation - explains all validation rules"""
    return render_template('documentation_v2.html')


@app.route('/templates')
def templates():
    """Templates & Data Dictionaries - CSV templates and field specifications"""
    return render_template('templates_resources.html')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/api/systems')
def api_systems():
    """API: Get all data streams"""
    streams = DataStream.get_enabled_streams()
    return jsonify([stream.to_dict() for stream in streams])


@app.route('/api/submissions')
def api_submissions():
    """API: Get all submissions"""
    submissions = load_submissions()
    return jsonify(submissions)


@app.route('/api/submissions/<system_id>')
def api_system_submissions(system_id):
    """API: Get submissions for a specific system"""
    submissions = get_submissions_by_system(system_id)
    return jsonify(submissions)


@app.route('/api/jurisdictions/<state_abbr>')
def api_jurisdiction_data(state_abbr):
    """API: Get data for a specific jurisdiction"""
    submissions = get_submissions_by_jurisdiction(state_abbr)
    return jsonify(submissions)


@app.route('/api/system-status')
def api_system_status():
    """API: Get health status for all systems"""
    streams = DataStream.get_enabled_streams()

    status = {}
    for stream in streams:
        health = get_system_health(stream.id)
        stats = get_submission_stats(stream.id)

        status[stream.id] = {
            'name': stream.name,
            'health': health,
            'stats': stats
        }

    return jsonify(status)


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/admin')
def admin():
    """Admin panel"""
    return render_template('admin.html')


@app.route('/api/clear-data', methods=['POST'])
def api_clear_data():
    """API: Clear all submission data (password protected)"""
    password = request.form.get('password', '')

    if password != config.ADMIN_PASSWORD:
        return jsonify({'error': 'Invalid password'}), 403

    success = clear_all_submissions()

    if success:
        return jsonify({'message': 'All data cleared successfully'})
    else:
        return jsonify({'error': 'Failed to clear data'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
