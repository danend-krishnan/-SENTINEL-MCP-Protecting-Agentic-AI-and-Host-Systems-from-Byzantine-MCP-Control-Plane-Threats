"""
Attack Flow Visualization Generator
Creates Mermaid sequence diagrams showing attack progression
"""

from typing import Dict, List, Any, Optional


class AttackFlowVisualizer:
    """Generate visual representations of attack flows"""
    
    def __init__(self):
        self.scenarios_data = []
    
    def generate_mermaid_diagram(self, scenario_name: str, attack_flow: List[Dict],
                                  blocked: bool) -> str:
        """
        Generate Mermaid sequence diagram for attack flow
        
        Args:
            scenario_name: Name of the attack scenario
            attack_flow: List of steps in the attack
            blocked: Whether attack was blocked
        
        Returns:
            Mermaid diagram markdown code
        """
        
        diagram = "sequenceDiagram\n"
        diagram += f"    Note over Agent,Security: {scenario_name}\n"
        
        # Show MCP Server initiating attack
        diagram += "    MCP Server->>Agent: Malicious Request\n"
        
        # Show security layer checking
        diagram += "    Agent->>Security Layer: Request Validation\n"
        diagram += "    activate Security Layer\n"
        
        # Add attack-specific flow steps
        for i, step in enumerate(attack_flow):
            action = step.get("action", "Unknown")
            component = step.get("component", "System")
            
            if i < len(attack_flow) - 1:
                diagram += f"    Security Layer->>Security Layer: Check {action}\n"
            else:
                if blocked:
                    diagram += "    Security Layer->>Agent:  BLOCKED\n"
                    diagram += "    deactivate Security Layer\n"
                    diagram += "    Agent->>MCP Server: Action Rejected\n"
                else:
                    diagram += "    Security Layer->>Agent: ✓ Allowed\n"
                    diagram += "    deactivate Security Layer\n"
                    diagram += f"    Agent->>System: Execute {component}\n"
        
        return diagram
    
    def generate_attack_sequence(self, scenario_data: Dict[str, Any]) -> List[Dict]:
        """
        Generate step-by-step attack sequence
        
        Returns:
            List of attack flow steps
        """
        scenario_id = scenario_data.get("scenario_id")
        scenario_type = scenario_data.get("scenario_type")
        
        # Define attack flows for each scenario type
        flows = {
            "command_injection": [
                {"action": "Parse Payload", "component": "MCP Message Handler", "step": 1},
                {"action": "Detect Command", "component": "Threat Pattern Matcher", "step": 2},
                {"action": "Check Policy", "component": "Policy Engine", "step": 3},
            ],
            "hidden_instructions": [
                {"action": "Scan Fields", "component": "Message Inspector", "step": 1},
                {"action": "Detect Hidden Field", "component": "Anomaly Detector", "step": 2},
                {"action": "Block Message", "component": "Decision Maker", "step": 3},
            ],
            "data_exfiltration": [
                {"action": "Check Path", "component": "File Access Filter", "step": 1},
                {"action": "Match Sensitive Path", "component": "Whitelist Checker", "step": 2},
                {"action": "Deny Access", "component": "Policy Engine", "step": 3},
            ],
            "privilege_escalation": [
                {"action": "Identify Request", "component": "Request Parser", "step": 1},
                {"action": "Check Privileges", "component": "Capability Validator", "step": 2},
                {"action": "Block Escalation", "component": "Security Gate", "step": 3},
            ],
            "instruction_chaining": [
                {"action": "Tokenize Input", "component": "Lexer", "step": 1},
                {"action": "Detect Chain Pattern", "component": "Pattern Matcher", "step": 2},
                {"action": "Reject Chain", "component": "Policy Engine", "step": 3},
            ],
            "fs_write": [
                {"action": "Identify Write Operation", "component": "FS Handler", "step": 1},
                {"action": "Check Write Policy", "component": "Policy Engine", "step": 2},
                {"action": "Block Write", "component": "Access Controller", "step": 3},
            ],
            "context_pollution": [
                {"action": "Scan Context", "component": "Context Analyzer", "step": 1},
                {"action": "Detect Anomaly", "component": "Anomaly Detector", "step": 2},
                {"action": "Filter Context", "component": "Context Sanitizer", "step": 3},
            ],
            "os_gathering": [
                {"action": "Detect Query", "component": "Query Parser", "step": 1},
                {"action": "Check Sensitivity", "component": "Sensitivity Classifier", "step": 2},
                {"action": "Log & Allow", "component": "Audit System", "step": 3},
            ],
        }
        
        return flows.get(scenario_type, flows["command_injection"])
    
    def create_scenario_visualization(self, scenario_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create complete visualization data for a scenario
        
        Returns:
            Dict with mermaid code and metadata
        """
        scenario_type = scenario_data.get("scenario_type")
        blocked = scenario_data.get("blocked", False)
        
        attack_flow = self.generate_attack_sequence(scenario_data)
        mermaid_code = self.generate_mermaid_diagram(
            scenario_type,
            attack_flow,
            blocked
        )
        
        return {
            "scenario_id": scenario_data.get("scenario_id"),
            "scenario_type": scenario_type,
            "blocked": blocked,
            "mermaid_diagram": mermaid_code,
            "attack_flow_steps": attack_flow,
            "timestamp": scenario_data.get("timestamp", "N/A")
        }
    
    def generate_summary_statistics(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """Generate summary statistics from all scenarios"""
        total = len(scenarios)
        blocked = sum(1 for s in scenarios if s.get("blocked"))
        
        return {
            "total_scenarios": total,
            "blocked_count": blocked,
            "allowed_count": total - blocked,
            "blocking_percentage": round((blocked / total * 100), 1) if total > 0 else 0,
        }
