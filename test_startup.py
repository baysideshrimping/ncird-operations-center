"""
Quick test script to verify the app can start
"""
import sys
print("=" * 60)
print("NCIRD Operations Center - Startup Test")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    import flask
    print("   [OK] Flask imported")
except Exception as e:
    print(f"   [ERROR] Flask import failed: {e}")
    sys.exit(1)

try:
    import pandas
    print("   [OK] Pandas imported")
except Exception as e:
    print(f"   [ERROR] Pandas import failed: {e}")
    sys.exit(1)

try:
    import config
    print("   [OK] Config imported")
except Exception as e:
    print(f"   [ERROR] Config import failed: {e}")
    sys.exit(1)

try:
    from models import ValidationResult, DataStream
    print("   [OK] Models imported")
except Exception as e:
    print(f"   [ERROR] Models import failed: {e}")
    sys.exit(1)

try:
    from validators import get_validator
    print("   [OK] Validators imported")
except Exception as e:
    print(f"   [ERROR] Validators import failed: {e}")
    sys.exit(1)

# Test app import
print("\n2. Testing app import...")
try:
    import app as main_app
    print("   [OK] App imported successfully")
except Exception as e:
    print(f"   [ERROR] App import failed: {e}")
    sys.exit(1)

# Test data directories
print("\n3. Checking data directories...")
import os
if os.path.exists('data'):
    print("   [OK] data/ directory exists")
else:
    print("   [ERROR] data/ directory missing - creating...")
    os.makedirs('data', exist_ok=True)

if os.path.exists('data/submissions'):
    print("   [OK] data/submissions/ directory exists")
else:
    print("   [ERROR] data/submissions/ directory missing - creating...")
    os.makedirs('data/submissions', exist_ok=True)

if os.path.exists('data/submissions.json'):
    print("   [OK] data/submissions.json exists")
else:
    print("   [ERROR] data/submissions.json missing - creating...")
    with open('data/submissions.json', 'w') as f:
        f.write('[]')

# Check enabled systems
print("\n4. Checking configured systems...")
from models import DataStream
enabled_streams = DataStream.get_enabled_streams()
print(f"   [OK] {len(enabled_streams)} enabled data streams found:")
for stream in enabled_streams[:5]:
    print(f"      - {stream.name}")
if len(enabled_streams) > 5:
    print(f"      ... and {len(enabled_streams) - 5} more")

# All good!
print("\n" + "=" * 60)
print("[OK] ALL CHECKS PASSED!")
print("=" * 60)
print("\nYou can now start the application:")
print("  python app.py")
print("\nThen open in your browser:")
print("  http://localhost:5000")
print("  or")
print("  http://127.0.0.1:5000")
print("=" * 60)
