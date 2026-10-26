"""
ClientOps AI - Unified Application Launcher
Starts the ClientOps AI server with FastAPI + OpenAPI Swagger (/docs) and Enterprise UI.
"""

import os
import sys
from pathlib import Path
import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("\n" + "=" * 76)
    print("  Starting ClientOps AI Enterprise Platform")
    print("  * Interactive UI:      http://127.0.0.1:8000/")
    print("  * Swagger OpenAPI Doc: http://127.0.0.1:8000/docs")
    print("  * Health Monitoring:   http://127.0.0.1:8000/api/health")
    print("  * watsonx.ai Model:    ibm/granite-3-8b-instruct")
    print("=" * 76 + "\n")
    
    uvicorn.run("app.api:app", host=host, port=port, reload=False)
