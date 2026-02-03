"""Validation modules for NCIRD data streams"""

from .base_validator import BaseValidator
from .nnad_validator import NNADValidator
from .mumps_validator import MumpsValidator
from .nrevss_validator import NREVSSValidator

__all__ = [
    'BaseValidator',
    'NNADValidator',
    'MumpsValidator',
    'NREVSSValidator'
]

# Validator registry - maps system_id to validator class
VALIDATOR_REGISTRY = {
    'nnad': NNADValidator,
    'mumps': MumpsValidator,
    'nrevss': NREVSSValidator
}

def get_validator(system_id):
    """
    Get validator instance for a system

    Args:
        system_id: System identifier

    Returns:
        Validator instance or None
    """
    validator_class = VALIDATOR_REGISTRY.get(system_id)
    if validator_class:
        return validator_class()
    return None
