"""
Jurisdiction model
Represents a state, territory, or other reporting jurisdiction
"""

from utils.state_codes import (
    STATE_FIPS_CODES,
    STATE_ABBR_TO_FIPS,
    FIPS_TO_STATE_ABBR,
    validate_state_code,
    get_all_jurisdictions
)

class Jurisdiction:
    """
    Represents a US state, territory, or jurisdiction

    Handles FIPS codes, abbreviations, and names
    """

    def __init__(self, identifier, id_type='abbr'):
        """
        Initialize jurisdiction

        Args:
            identifier: FIPS code, abbreviation, or name
            id_type: 'fips', 'abbr', 'name', or 'iis'
        """
        self.data = validate_state_code(identifier, id_type)

        if not self.data:
            raise ValueError(f"Invalid jurisdiction: {identifier}")

    @property
    def fips(self):
        return self.data['fips']

    @property
    def abbr(self):
        return self.data['abbr']

    @property
    def name(self):
        return self.data['name']

    @property
    def iis_code(self):
        return self.data.get('iis_code')

    def to_dict(self):
        """Convert to dictionary"""
        return self.data

    @classmethod
    def get_all(cls):
        """Get all jurisdictions"""
        return get_all_jurisdictions()

    @classmethod
    def from_abbr(cls, abbr):
        """Create from abbreviation"""
        return cls(abbr, 'abbr')

    @classmethod
    def from_fips(cls, fips):
        """Create from FIPS code"""
        return cls(fips, 'fips')

    @classmethod
    def from_iis_code(cls, iis_code):
        """Create from IIS grantee code"""
        return cls(iis_code, 'iis')

    def __repr__(self):
        return f"<Jurisdiction {self.abbr} {self.name}>"

    def __str__(self):
        return f"{self.name} ({self.abbr})"
