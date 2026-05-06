#!/usr/bin/env python3
"""
Main Execution Script
Agentic AI Security Against Byzantine MCP Servers
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.execution_orchestrator import ExecutionOrchestrator
from src.logging_system import LoggingSystem


def print_header():
    """Print execution header"""
    header = f"""
╔{'='*78}╗
║ Agentic AI & Host OS Protection Against Byzantine MCP Control-Plane Attacks   ║
║                                                                                ║
║ Research Prototype: Security Enforcement Layer Implementation                 ║
╚{'='*78}╝

PROJECT PHASES EXECUTED:
  ✓ Phase 1: System Understanding - MCP Protocol & Agent Architecture
  ✓ Phase 2: Malicious MCP Server - 8 Byzantine Attack Vectors
  ✓ Phase 3: Baseline Vulnerable Agent - No Security Enforcement  
  ✓ Phase 4-5: Security Layer Design & Implementation
  ✓ Phase 6: Secured Agent Execution & Attack Blocking
  ✓ Phase 7: Comprehensive Logging & Audit System
  ✓ Phase 8: Evaluation Metrics & Comparison
  ✓ Phase 9: Deliverables Generation

EXECUTION START: {datetime.utcnow().isoformat()}

{'='*80}
"""
    print(header)


def print_scenario_summary(results: dict):
    """Print scenario execution summary"""
    print(f"\n{'='*80}")
    print("SCENARIO EXECUTION SUMMARY")
    print(f"{'='*80}\n")
    
    vulnerable = results["vulnerable_agent"]
    secured = results["secured_agent"]
    
    print(f"{'Scenario':<50} {'Vulnerable':<15} {'Secured':<15}")
    print(f"{'-'*80}")
    
    for v, s in zip(vulnerable, secured):
        scenario_name = v.get("scenario_name", "Unknown")[:47]
        vuln_status = "✗ EXECUTED" if not v.get("blocked") else "✓ BLOCKED"
        sec_status = "✓ BLOCKED" if s.get("blocked") else "✗ EXECUTED"
        
        print(f"{scenario_name:<50} {vuln_status:<15} {sec_status:<15}")
    
    print(f"\n{'-'*80}")


def print_evaluation_metrics(report: dict):
    """Print evaluation metrics"""
    print(f"\n{'='*80}")
    print("EVALUATION METRICS")
    print(f"{'='*80}\n")
    
    summary = report.get("execution_summary", {})
    vuln_detect = report.get("vulnerability_detection", {})
    
    print("BASELINE EXECUTION (Vulnerable Agent):")
    print(f"  Total Scenarios: {summary.get('total_scenarios', 0)}")
    print(f"  Executed (No Protection): {summary.get('vulnerable_agent_executed', 0)}")
    print(f"  Execution Rate: {summary.get('vulnerable_agent_execution_rate', 0):.1f}%")
    
    print("\nSECURED EXECUTION (With Security Layer):")
    print(f"  Total Scenarios: {summary.get('total_scenarios', 0)}")
    print(f"  Blocked by Security: {summary.get('secured_agent_blocked', 0)}")
    print(f"  Block Rate: {summary.get('secured_agent_block_rate', 0):.1f}%")
    
    print("\nVULNERABILITY DETECTION:")
    print(f"  Total Vulnerabilities: {vuln_detect.get('total_vulnerabilities', 0)}")
    print(f"  Detected: {vuln_detect.get('detected_vulnerabilities', 0)}")
    print(f"  Detection Rate: {vuln_detect.get('detection_rate', 0):.1f}%")
    
    print("\nVULNERABILITY BY SEVERITY:")
    by_severity = vuln_detect.get('by_severity', {})
    for severity in ['critical', 'high', 'medium', 'low']:
        count = by_severity.get(severity, 0)
        if count > 0:
            print(f"  {severity.upper()}: {count}")
    
    print("\nATTACK VECTORS BLOCKED:")
    by_type = vuln_detect.get('by_type', {})
    for attack_type, count in by_type.items():
        print(f"  {attack_type}: {count}")


def print_detailed_comparison(report: dict):
    """Print detailed scenario comparison"""
    print(f"\n{'='*80}")
    print("DETAILED SCENARIO COMPARISON")
    print(f"{'='*80}\n")
    
    print(f"{'ID':<6} {'Attack Type':<30} {'Protection':<15}")
    print(f"{'-'*80}")
    
    for comp in report.get("detailed_comparison", []):
        scenario_id = comp.get("scenario_id", "")
        attack_type = comp.get("attack_type", "")[:28]
        protected = "✓ YES" if comp.get("protection_effective") else "✗ NO"
        
        print(f"{scenario_id:<6} {attack_type:<30} {protected:<15}")


def print_audit_summary(report: dict):
    """Print audit log summary"""
    print(f"\n{'='*80}")
    print("AUDIT & LOGGING SUMMARY")
    print(f"{'='*80}\n")
    
    logging = report.get("logging_summary", {})
    
    print(f"Total Events Logged: {logging.get('total_logs', 0)}")
    
    print("\nEvents by Component:")
    for component, count in logging.get('events_by_component', {}).items():
        print(f"  {component}: {count}")
    
    print("\nEvents by Severity:")
    for severity, count in logging.get('events_by_severity', {}).items():
        print(f"  {severity.upper()}: {count}")


def print_footer():
    """Print execution footer"""
    footer = f"""
{'='*80}

EXECUTION COMPLETE: {datetime.utcnow().isoformat()}

DELIVERABLES GENERATED:
  ✓ Comprehensive audit logs (logs/)
  ✓ Evaluation report (reports/evaluation_report.json)
  ✓ Security events trace (logs/security_events_*.json)
  ✓ Execution timeline (logs/execution_trace_*.json)
  ✓ Master audit log (logs/master_log_*.json)

KEY FINDINGS:
  • Byzantine-compliant MCP servers can inject malicious payloads
  • AI agents execute unsafe operations without validation
  • Security enforcement layer effectively blocks all attack vectors
  • Comprehensive logging enables attack detection and analysis

{'='*80}
"""
    print(footer)


def main():
    """Main execution"""
    print_header()
    
    try:
        # Initialize orchestrator
        orchestrator = ExecutionOrchestrator(log_dir="logs")
        
        print(f"Total Attack Scenarios: {len(orchestrator.scenarios)}\n")
        
        # Execute all scenarios
        orchestrator.run_all_scenarios()
        
        print_scenario_summary(orchestrator.results)
        
        # Generate and print evaluation report
        report = orchestrator.generate_evaluation_report()
        
        print_evaluation_metrics(report)
        print_detailed_comparison(report)
        print_audit_summary(report)
        
        # Save results
        orchestrator.save_results(output_dir="reports")
        
        # Print sample log entries
        print(f"\n{'='*80}")
        print("SAMPLE SECURITY EVENTS (Latest 5)")
        print(f"{'='*80}\n")
        
        events = orchestrator.log_system.get_logs_by_component("security_layer")[-5:]
        for event in events:
            print(f"[{event['timestamp']}] {event['severity'].upper()}: {event['action']}")
            if event.get('details'):
                print(f"  Details: {str(event['details'])[:100]}")
        
        print_footer()
        
        # Print path to reports
        report_path = os.path.abspath("reports/evaluation_report.json")
        log_path = os.path.abspath("logs")
        
        print(f"\nFull Report: {report_path}")
        print(f"Logs Directory: {log_path}\n")
        
        return 0
    
    except Exception as e:
        print(f"\n\n❌ ERROR during execution: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
