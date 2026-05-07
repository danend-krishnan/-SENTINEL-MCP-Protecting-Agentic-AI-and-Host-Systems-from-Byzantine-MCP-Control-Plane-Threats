"""
Comprehensive Logging & Audit System
Tracks all security events, agent actions, and MCP messages
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class LoggingSystem:
    """Centralized audit logging for security events"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.logs: List[Dict[str, Any]] = []
        self.start_time = datetime.utcnow()
    
    def log_event(self, component: str, action: str, severity: str = "INFO",
                  details: Optional[Dict] = None, blocked: bool = False):
        """Log a security or operational event"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "component": component,
            "action": action,
            "severity": severity,
            "details": details or {},
            "blocked": blocked
        }
        self.logs.append(event)
        return event
    
    def get_logs_by_component(self, component: str) -> List[Dict]:
        """Get all logs for a specific component"""
        return [log for log in self.logs if log.get("component") == component]
    
    def get_logs_by_severity(self, severity: str) -> List[Dict]:
        """Get all logs for a specific severity level"""
        return [log for log in self.logs if log.get("severity") == severity]
    
    def get_security_events(self) -> List[Dict]:
        """Get all security-related events"""
        return self.get_logs_by_component("security_layer")
    
    def save_logs(self, prefix: str = "master_log"):
        """Save all logs to JSON file"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = self.log_dir / f"{prefix}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.logs, f, indent=2)
        
        return filename
    
    def get_summary(self) -> Dict[str, Any]:
        """Get audit summary statistics"""
        return {
            "total_logs": len(self.logs),
            "events_by_component": self._count_by_key("component"),
            "events_by_severity": self._count_by_key("severity"),
            "total_blocked": sum(1 for log in self.logs if log.get("blocked")),
        }
    
    def _count_by_key(self, key: str) -> Dict[str, int]:
        """Count events by a specific key"""
        counts = {}
        for log in self.logs:
            val = log.get(key)
            if val:
                counts[val] = counts.get(val, 0) + 1
        return counts
