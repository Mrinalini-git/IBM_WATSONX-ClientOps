"""
Run the ClientOps AI Flask API Server.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.flask_app import flask_app

if __name__ == "__main__":
    port = 5000
    print("\n" + "=" * 70)
    print("  Starting ClientOps AI Flask Server")
    print(f"  * Frontend & API: http://127.0.0.1:{port}/")
    print(f"  * Health Check:   http://127.0.0.1:{port}/api/health")
    print(f"  * Analysis API:   http://127.0.0.1:{port}/api/analyze")
    print("=" * 70 + "\n")
    flask_app.run(host="0.0.0.0", port=port, debug=False)
