"""
State, territory, and jurisdiction codes and mappings
Includes FIPS codes, abbreviations, and names
"""

# State FIPS codes (numeric to name)
STATE_FIPS_CODES = {
    1: 'Alabama', 2: 'Alaska', 4: 'Arizona', 5: 'Arkansas', 6: 'California',
    8: 'Colorado', 9: 'Connecticut', 10: 'Delaware', 11: 'District of Columbia',
    12: 'Florida', 13: 'Georgia', 15: 'Hawaii', 16: 'Idaho', 17: 'Illinois',
    18: 'Indiana', 19: 'Iowa', 20: 'Kansas', 21: 'Kentucky', 22: 'Louisiana',
    23: 'Maine', 24: 'Maryland', 25: 'Massachusetts', 26: 'Michigan',
    27: 'Minnesota', 28: 'Mississippi', 29: 'Missouri', 30: 'Montana',
    31: 'Nebraska', 32: 'Nevada', 33: 'New Hampshire', 34: 'New Jersey',
    35: 'New Mexico', 36: 'New York', 37: 'North Carolina', 38: 'North Dakota',
    39: 'Ohio', 40: 'Oklahoma', 41: 'Oregon', 42: 'Pennsylvania',
    44: 'Rhode Island', 45: 'South Carolina', 46: 'South Dakota', 47: 'Tennessee',
    48: 'Texas', 49: 'Utah', 50: 'Vermont', 51: 'Virginia', 53: 'Washington',
    54: 'West Virginia', 55: 'Wisconsin', 56: 'Wyoming',
    # Territories
    60: 'American Samoa', 66: 'Guam', 69: 'Northern Mariana Islands',
    72: 'Puerto Rico', 78: 'Virgin Islands'
}

# State abbreviations to FIPS
STATE_ABBR_TO_FIPS = {
    'AL': 1, 'AK': 2, 'AZ': 4, 'AR': 5, 'CA': 6, 'CO': 8, 'CT': 9, 'DE': 10,
    'DC': 11, 'FL': 12, 'GA': 13, 'HI': 15, 'ID': 16, 'IL': 17, 'IN': 18,
    'IA': 19, 'KS': 20, 'KY': 21, 'LA': 22, 'ME': 23, 'MD': 24, 'MA': 25,
    'MI': 26, 'MN': 27, 'MS': 28, 'MO': 29, 'MT': 30, 'NE': 31, 'NV': 32,
    'NH': 33, 'NJ': 34, 'NM': 35, 'NY': 36, 'NC': 37, 'ND': 38, 'OH': 39,
    'OK': 40, 'OR': 41, 'PA': 42, 'RI': 44, 'SC': 45, 'SD': 46, 'TN': 47,
    'TX': 48, 'UT': 49, 'VT': 50, 'VA': 51, 'WA': 53, 'WV': 54, 'WI': 55,
    'WY': 56,
    # Territories
    'AS': 60, 'GU': 66, 'MP': 69, 'PR': 72, 'VI': 78
}

# FIPS to abbreviation
FIPS_TO_STATE_ABBR = {v: k for k, v in STATE_ABBR_TO_FIPS.items()}

# State names to abbreviations
STATE_NAME_TO_ABBR = {v: k for k, v in {
    **{FIPS_TO_STATE_ABBR[fips]: name for fips, name in STATE_FIPS_CODES.items()}
}.items()}

# All valid state abbreviations (for validation)
VALID_STATE_ABBRS = set(STATE_ABBR_TO_FIPS.keys())

# Continental US states only (excluding AK, HI, territories)
CONTINENTAL_US_ABBRS = {
    'AL', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'ID', 'IL',
    'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO',
    'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR',
    'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
}

# CDC IIS grantee codes (3-letter codes used in some systems)
IIS_GRANTEE_CODES = {
    'BAA': 'New York City', 'CAA': 'California', 'CBA': 'Chicago',
    'CCA': 'Colorado', 'CDA': 'Connecticut', 'DEA': 'Delaware',
    'DCA': 'District of Columbia', 'FLA': 'Florida', 'GAA': 'Georgia',
    'HIA': 'Hawaii', 'IDA': 'Idaho', 'ILA': 'Illinois', 'INA': 'Indiana',
    'IAA': 'Iowa', 'KSA': 'Kansas', 'KYA': 'Kentucky', 'LAA': 'Louisiana',
    'MEA': 'Maine', 'MDA': 'Maryland', 'MAA': 'Massachusetts', 'MIA': 'Michigan',
    'MNA': 'Minnesota', 'MSA': 'Mississippi', 'MOA': 'Missouri', 'MTA': 'Montana',
    'NEA': 'Nebraska', 'NVA': 'Nevada', 'NHA': 'New Hampshire', 'NJA': 'New Jersey',
    'NMA': 'New Mexico', 'NYA': 'New York', 'NCA': 'North Carolina',
    'NDA': 'North Dakota', 'OHA': 'Ohio', 'OKA': 'Oklahoma', 'ORA': 'Oregon',
    'PAA': 'Pennsylvania', 'PBA': 'Philadelphia', 'RIA': 'Rhode Island',
    'SCA': 'South Carolina', 'SDA': 'South Dakota', 'TNA': 'Tennessee',
    'TXA': 'Texas', 'TBA': 'Houston', 'UTA': 'Utah', 'VTA': 'Vermont',
    'VAA': 'Virginia', 'WAA': 'Washington', 'WVA': 'West Virginia',
    'WIA': 'Wisconsin', 'WYA': 'Wyoming',
    # Territories
    'ASA': 'American Samoa', 'GUA': 'Guam', 'MPA': 'Northern Mariana Islands',
    'PRA': 'Puerto Rico', 'VIA': 'Virgin Islands', 'RSI': 'Republic of Palau',
    'FSM': 'Federated States of Micronesia', 'RMI': 'Republic of Marshall Islands'
}

# Reverse lookup for IIS codes
IIS_CODE_TO_ABBR = {
    'BAA': 'NY', 'CAA': 'CA', 'CBA': 'IL', 'CCA': 'CO', 'CDA': 'CT', 'DEA': 'DE',
    'DCA': 'DC', 'FLA': 'FL', 'GAA': 'GA', 'HIA': 'HI', 'IDA': 'ID', 'ILA': 'IL',
    'INA': 'IN', 'IAA': 'IA', 'KSA': 'KS', 'KYA': 'KY', 'LAA': 'LA', 'MEA': 'ME',
    'MDA': 'MD', 'MAA': 'MA', 'MIA': 'MI', 'MNA': 'MN', 'MSA': 'MS', 'MOA': 'MO',
    'MTA': 'MT', 'NEA': 'NE', 'NVA': 'NV', 'NHA': 'NH', 'NJA': 'NJ', 'NMA': 'NM',
    'NYA': 'NY', 'NCA': 'NC', 'NDA': 'ND', 'OHA': 'OH', 'OKA': 'OK', 'ORA': 'OR',
    'PAA': 'PA', 'PBA': 'PA', 'RIA': 'RI', 'SCA': 'SC', 'SDA': 'SD', 'TNA': 'TN',
    'TXA': 'TX', 'TBA': 'TX', 'UTA': 'UT', 'VTA': 'VT', 'VAA': 'VA', 'WAA': 'WA',
    'WVA': 'WV', 'WIA': 'WI', 'WYA': 'WY', 'ASA': 'AS', 'GUA': 'GU', 'MPA': 'MP',
    'PRA': 'PR', 'VIA': 'VI'
}

def validate_state_code(code, code_type='abbr'):
    """
    Validate a state code and return standardized info

    Args:
        code: State code (FIPS, abbreviation, or IIS code)
        code_type: 'fips', 'abbr', or 'iis'

    Returns:
        dict with fips, abbr, name or None if invalid
    """
    if code_type == 'fips':
        fips = int(code) if isinstance(code, str) else code
        if fips in STATE_FIPS_CODES:
            return {
                'fips': fips,
                'abbr': FIPS_TO_STATE_ABBR[fips],
                'name': STATE_FIPS_CODES[fips]
            }
    elif code_type == 'abbr':
        code = code.upper()
        if code in STATE_ABBR_TO_FIPS:
            fips = STATE_ABBR_TO_FIPS[code]
            return {
                'fips': fips,
                'abbr': code,
                'name': STATE_FIPS_CODES[fips]
            }
    elif code_type == 'iis':
        code = code.upper()
        if code in IIS_GRANTEE_CODES:
            abbr = IIS_CODE_TO_ABBR.get(code)
            if abbr and abbr in STATE_ABBR_TO_FIPS:
                fips = STATE_ABBR_TO_FIPS[abbr]
                return {
                    'fips': fips,
                    'abbr': abbr,
                    'name': STATE_FIPS_CODES[fips],
                    'iis_code': code,
                    'jurisdiction': IIS_GRANTEE_CODES[code]
                }
    return None

def get_all_jurisdictions():
    """Return list of all valid jurisdictions"""
    return [
        {
            'fips': fips,
            'abbr': FIPS_TO_STATE_ABBR[fips],
            'name': name
        }
        for fips, name in STATE_FIPS_CODES.items()
    ]
