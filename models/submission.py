"""
Submission model
Tracks file uploads and validation requests
"""

from datetime import datetime
from .validation_result import ValidationResult

class Submission:
    """
    Represents a data submission to the system

    A submission encompasses:
    - The uploaded file
    - System/stream it belongs to
    - Validation results
    - Tracking metadata
    """

    def __init__(self, system_id, filename, file_path):
        self.system_id = system_id
        self.filename = filename
        self.file_path = file_path
        self.upload_time = datetime.now()
        self.validation_result = None
        self.user_info = {}

    def set_validation_result(self, validation_result):
        """Attach validation result"""
        self.validation_result = validation_result

    def to_dict(self):
        """Convert to dictionary"""
        data = {
            'system_id': self.system_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'upload_time': self.upload_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user_info': self.user_info
        }

        if self.validation_result:
            data['validation'] = self.validation_result.to_dict()

        return data

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        submission = cls(
            data['system_id'],
            data['filename'],
            data['file_path']
        )
        submission.upload_time = datetime.strptime(
            data['upload_time'],
            '%Y-%m-%d %H:%M:%S'
        )
        submission.user_info = data.get('user_info', {})

        if 'validation' in data:
            submission.validation_result = ValidationResult.from_dict(data['validation'])

        return submission
