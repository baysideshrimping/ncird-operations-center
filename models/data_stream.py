"""
DataStream model
Represents a CDC data surveillance system
"""

from config import DATA_STREAMS

class DataStream:
    """
    Represents an NCIRD data stream/surveillance system

    Examples: NNAD, Mumps, NREVSS, NIS, etc.
    """

    def __init__(self, stream_id):
        self.id = stream_id
        self.config = DATA_STREAMS.get(stream_id, {})

    @property
    def name(self):
        return self.config.get('name', self.id.upper())

    @property
    def full_name(self):
        return self.config.get('full_name', '')

    @property
    def description(self):
        return self.config.get('description', '')

    @property
    def category(self):
        return self.config.get('category', 'Other')

    @property
    def enabled(self):
        return self.config.get('enabled', False)

    @property
    def priority(self):
        return self.config.get('priority', 99)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            **self.config
        }

    @classmethod
    def get_all_streams(cls):
        """Get all defined data streams"""
        return [cls(stream_id) for stream_id in DATA_STREAMS.keys()]

    @classmethod
    def get_enabled_streams(cls):
        """Get only enabled streams"""
        return [stream for stream in cls.get_all_streams() if stream.enabled]

    def __repr__(self):
        return f"<DataStream {self.id} {self.name}>"
