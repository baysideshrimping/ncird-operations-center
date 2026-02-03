"""
ValidationResult model
Stores the outcome of a validation run including errors, warnings, and metadata
"""

import uuid
from datetime import datetime

class ValidationResult:
    """
    Stores validation results for a single submission

    Attributes:
        submission_id: Unique identifier
        system_id: Data stream identifier (nnad, mumps, etc.)
        filename: Original uploaded filename
        timestamp: When validation occurred
        status: 'passed', 'passed_with_warnings', 'failed', 'pending'
        jurisdiction: State/territory code
        errors: List of error dicts
        warnings: List of warning dicts
        info_messages: List of informational messages
        row_count: Number of data rows processed
        metadata: Additional context (file size, format, etc.)
    """

    def __init__(self, system_id, filename):
        self.submission_id = str(uuid.uuid4())[:8]
        self.system_id = system_id
        self.filename = filename
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status = 'pending'
        self.jurisdiction = None
        self.errors = []
        self.warnings = []
        self.info_messages = []
        self.row_count = 0
        self.metadata = {}

    def add_error(self, message, row=None, field=None, severity='error'):
        """
        Add an error to the result

        Args:
            message: Error description
            row: Optional row number (1-indexed)
            field: Optional field/column name
            severity: 'error', 'warning', or 'info'
        """
        error_obj = {
            'message': message,
            'severity': severity
        }

        if row is not None:
            error_obj['row'] = row

        if field is not None:
            error_obj['field'] = field

        if severity == 'error':
            self.errors.append(error_obj)
        elif severity == 'warning':
            self.warnings.append(error_obj)
        else:
            self.info_messages.append(error_obj)

    def add_warning(self, message, row=None, field=None):
        """Convenience method to add a warning"""
        self.add_error(message, row, field, severity='warning')

    def add_info(self, message, row=None, field=None):
        """Convenience method to add an info message"""
        self.add_error(message, row, field, severity='info')

    def set_metadata(self, key, value):
        """Add metadata key-value pair"""
        self.metadata[key] = value

    def determine_status(self):
        """
        Determine overall status based on errors and warnings

        Returns:
            'passed', 'passed_with_warnings', or 'failed'
        """
        if len(self.errors) > 0:
            self.status = 'failed'
        elif len(self.warnings) > 0:
            self.status = 'passed_with_warnings'
        else:
            self.status = 'passed'

        return self.status

    def get_error_summary(self):
        """Get summary of errors by field"""
        summary = {}

        for error in self.errors:
            field = error.get('field', 'General')
            if field not in summary:
                summary[field] = 0
            summary[field] += 1

        return summary

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'submission_id': self.submission_id,
            'system_id': self.system_id,
            'filename': self.filename,
            'timestamp': self.timestamp,
            'status': self.status,
            'jurisdiction': self.jurisdiction,
            'errors': self.errors,
            'warnings': self.warnings,
            'info_messages': self.info_messages,
            'row_count': self.row_count,
            'metadata': self.metadata,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'error_summary': self.get_error_summary()
        }

    @classmethod
    def from_dict(cls, data):
        """Create ValidationResult from dictionary"""
        result = cls(data['system_id'], data['filename'])
        result.submission_id = data['submission_id']
        result.timestamp = data['timestamp']
        result.status = data['status']
        result.jurisdiction = data.get('jurisdiction')
        result.errors = data.get('errors', [])
        result.warnings = data.get('warnings', [])
        result.info_messages = data.get('info_messages', [])
        result.row_count = data.get('row_count', 0)
        result.metadata = data.get('metadata', {})
        return result

    def __repr__(self):
        return f"<ValidationResult {self.submission_id} {self.system_id} {self.status}>"
