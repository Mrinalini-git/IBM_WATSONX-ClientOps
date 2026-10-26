"""
ClientOps AI - Working Demo Progression Script
Demonstrates the complete enterprise pipeline:
1. Synthetic Enterprise ITSM Data Generation (IBM Graph RAG generator)
2. Ingestion & Persistence (SQLite / PostgreSQL)
3. IBM Granite Foundation Model Analysis (watsonx.ai)
4. Structured Diagnostic Playbook & Human Verification Mandate
5. Enterprise FastAPI Service Verification
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.generator import ITSMDataGenerator
from app.database import init_db, SessionLocal
from app.models import IncidentModel, AnalysisResultModel
from app.watsonx_client import granite_client, HUMAN_VERIFICATION_MANDATE


def print_banner(text: str):
    print("\n" + "=" * 78)
    print(f"  {text}")
    print("=" * 78)


def step_1_generate_synthetic_itsm():
    print_banner("STEP 1: GENERATE SYNTHETIC ENTERPRISE ITSM DATA (IBM REPOSITORY)")
    print("Invoking official IBM Enterprise ITSM generator...")
    print("Source: https://github.com/IBM/enterprise-itsm-graph-rag\n")
    
    gen = ITSMDataGenerator()
    data_dir = Path(__file__).resolve().parent / "data"
    bundle = gen.save_datasets(str(data_dir), incident_count=20)
    
    counts = bundle["metadata"]["counts"]
    print(f"\n[Generated Graph Entities]")
    print(f"  • Business Services:    {counts['services']}")
    print(f"  • Configuration Items:  {counts['cis']}")
    print(f"  • Incidents:            {counts['incidents']}")
    print(f"  • Problem Records:      {counts['problems']}")
    print(f"  • Change Requests:      {counts['changes']}")
    print(f"  • KB Articles:          {counts['kb_articles']}")
    
    sample_inc = bundle["incidents"][0]
    print(f"\n[Sample Synthetic Incident Extracted]")
    print(f"  Ticket Number:  {sample_inc['number']}")
    print(f"  Summary:        {sample_inc['short_description']}")
    print(f"  Affected CI:    {sample_inc['affected_ci']}")
    print(f"  Priority:       {sample_inc['priority']} (Impact: {sample_inc['impact']})")
    
    return sample_inc


def step_2_database_persistence():
    print_banner("STEP 2: DATABASE PERSISTENCE (SQLAlchemy SQLite / PostgreSQL)")
    init_db()
    db = SessionLocal()
    total_incidents = db.query(IncidentModel).count()
    print(f"Database successfully synchronized.")
    print(f"Current total incidents in persistent storage: {total_incidents}")
    
    # Pick a critical incident for analysis
    target = db.query(IncidentModel).filter(IncidentModel.priority.in_(["P1", "P2"])).first()
    if not target:
        target = db.query(IncidentModel).first()
    
    incident_dict = target.to_dict()
    db.close()
    return incident_dict


def step_3_watsonx_granite_analysis(incident_dict):
    print_banner("STEP 3: IBM watsonx.ai GRANITE FOUNDATION MODEL ANALYSIS")
    print(f"Target Incident: {incident_dict['number']} on '{incident_dict['affected_ci']}'")
    print(f"Model: {granite_client.model_id}")
    print(f"Provider: {granite_client.is_live_configured() and 'Live IBM Cloud' or 'Ready Mode (Granite Simulation)'}")
    print("\nSending prompt to Granite model...")
    
    t0 = time.time()
    analysis = granite_client.analyze_incident(incident_dict)
    latency = round((time.time() - t0) * 1000, 1)
    
    print(f"Analysis completed in {latency} ms!\n")
    return analysis


def step_4_display_demo_output(analysis):
    print_banner("STEP 4: CLIENTOPS AI DEMO OUTPUT")
    
    orig = analysis["original_incident"]
    print("--- 1. ORIGINAL SYNTHETIC INCIDENT ---")
    print(f"Ticket:      {orig.get('number')}")
    print(f"Affected CI: {orig.get('affected_ci')}")
    print(f"Priority:    {orig.get('priority')} (Impact: {orig.get('impact', 'High')})")
    print(f"Description: {orig.get('short_description')}")
    print(f"Full Logs:   {orig.get('detailed_description')}\n")
    
    print("--- 2. AI-GENERATED SUMMARY (IBM Granite) ---")
    print(f"{analysis['ai_summary']}\n")
    
    print("--- 3. POSSIBLE CAUSES ---")
    for i, cause in enumerate(analysis["possible_causes"], 1):
        print(f"  [{i}] {cause}")
    print()
    
    print("--- 4. DIAGNOSTIC & TROUBLESHOOTING STEPS ---")
    for i, step in enumerate(analysis["troubleshooting_steps"], 1):
        print(f"  Step {i}: {step}")
    print()
    
    print("--- 5. MANDATORY HUMAN VERIFICATION NOTE ---")
    print(f"  {analysis['human_verification_note']}\n")
    
    # Save to local file & DB
    db = SessionLocal()
    rec = AnalysisResultModel(
        id=analysis["analysis_id"],
        incident_id=orig.get("id"),
        incident_number=orig.get("number"),
        raw_input=orig.get("detailed_description"),
        summary=analysis["ai_summary"],
        possible_causes=json.dumps(analysis["possible_causes"]),
        troubleshooting_steps=json.dumps(analysis["troubleshooting_steps"]),
        human_verification_note=analysis["human_verification_note"],
        model_id=analysis["model_id"],
        provider=analysis["provider"],
        latency_ms=analysis["latency_ms"],
        created_at=analysis["analyzed_at"]
    )
    db.add(rec)
    db.commit()
    db.close()
    
    out_file = Path(__file__).resolve().parent / "data" / "demo_analysis_output.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(analysis, f, indent=2)
    print(f"[Saved Result] Local file written to: {out_file}")
    print(f"[Saved Result] Persisted to database 'analysis_results' table.")


def step_5_enterprise_fastapi():
    print_banner("STEP 5: ENTERPRISE FASTAPI SERVICE & DEPLOYABILITY")
    print("ClientOps AI exposes full OpenAPI / Swagger docs at:")
    print("  • Swagger UI: http://localhost:8000/docs")
    print("  • Frontend:   http://localhost:8000/")
    print("  • Analysis:   POST http://localhost:8000/api/analyze")
    print("  • Health:     GET  http://localhost:8000/api/health")
    print("\nTo launch the FastAPI server, run:")
    print("  uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload")
    print("=" * 78)


if __name__ == "__main__":
    step_1_generate_synthetic_itsm()
    incident = step_2_database_persistence()
    analysis = step_3_watsonx_granite_analysis(incident)
    step_4_display_demo_output(analysis)
    step_5_enterprise_fastapi()
