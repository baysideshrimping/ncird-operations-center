"""Run the app on port 8080 instead of 5000"""
from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("NCIRD Operations Center")
    print("=" * 60)
    print("\nStarting server on port 8080...")
    print("\nOpen in your browser:")
    print("  http://localhost:8080")
    print("  or")
    print("  http://127.0.0.1:8080")
    print("\nPress CTRL+C to stop")
    print("=" * 60)
    print()

    app.run(debug=True, host='0.0.0.0', port=8080)
