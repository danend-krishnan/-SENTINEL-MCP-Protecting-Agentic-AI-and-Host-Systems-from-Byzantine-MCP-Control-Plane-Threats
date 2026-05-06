# Security Enforcement Layer: Integration Guide & API Reference

## Table of Contents

1. [Quick Start](#quick-start)
2. [API Reference](#api-reference)
3. [Integration Patterns](#integration-patterns)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)
6. [Code Examples](#code-examples)

---

## Quick Start

### Installation

```bash
# Clone repository
cd project

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/macOS

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Basic Usage

```python
from src.security_enforcement_layer import SecurityEnforcementLayer
from src.logging_system import LoggingSystem

# Initialize security layer
security_layer = SecurityEnforcementLayer("my_agent")
security_layer.set_security_policy("BALANCED")

# Initialize logging
logger = LoggingSystem("logs")

# Validate MCP message
mcp_message = {
    "jsonrpc": "2.0",
    "id": "msg-001",
    "method": "tools/call",
    "params": {
        "name": "read_file",
        "arguments": {"path": "/home/user/data.txt"}
    }
}

is_valid, security_event = security_layer.validate_mcp_message(mcp_message)

if not is_valid:
    print(f"Message rejected: {security_event.message}")
    logger.log_security_event(
        event_type="message_rejected",
        severity="high",
        action="mcp_validation_failed",
        details={"reason": security_event.message}
    )
else:
    # Message is safe, proceed with action validation
    is_allowed, action_event = security_layer.validate_action(
        "file_read",
        {"path": "/home/user/data.txt"}
    )
    
    if is_allowed:
        print("Action approved - proceed with execution")
    else:
        print(f"Action blocked: {action_event.message}")
```

---

## API Reference

### SecurityEnforcementLayer

Main security enforcement component.

#### Constructor

```python
SecurityEnforcementLayer(agent_id: str)
```

**Parameters:**
- `agent_id` (str): Unique identifier for the agent

**Example:**
```python
security_layer = SecurityEnforcementLayer("secure_agent_001")
```

---

#### set_security_policy

```python
set_security_policy(policy_name: str) -> bool
```

Set the active security policy.

**Parameters:**
- `policy_name` (str): One of "RESTRICTIVE", "BALANCED", "PERMISSIVE"

**Returns:**
- `bool`: True if policy set successfully, False otherwise

**Example:**
```python
if security_layer.set_security_policy("BALANCED"):
    print("Policy set successfully")
else:
    print("Unknown policy name")
```

---

#### validate_mcp_message

```python
validate_mcp_message(message: Dict[str, Any]) -> Tuple[bool, Optional[SecurityEvent]]
```

Validate MCP message structure and content.

**Parameters:**
- `message` (Dict): MCP message to validate

**Returns:**
- `(bool, Optional[SecurityEvent])`: Validation result and security event if invalid

**Example:**
```python
is_valid, event = security_layer.validate_mcp_message(message)
if not is_valid:
    print(f"Validation failed: {event.message}")
```

---

#### validate_action

```python
validate_action(action_type: str, parameters: Dict[str, Any]) \
    -> Tuple[bool, Optional[SecurityEvent]]
```

Validate an action before execution.

**Parameters:**
- `action_type` (str): Type of action (e.g., "file_read", "command_execute")
- `parameters` (Dict): Action parameters

**Returns:**
- `(bool, Optional[SecurityEvent])`: Approval result and security event if denied

**Action Types:**
- `file_read`: Read file operation
- `file_write`: Write file operation
- `command_execute`: Execute system command
- `privilege_escalate`: Request privilege escalation
- `network_access`: Network access
- `system_query`: Query OS information
- `permission_modify`: Modify file/system permissions
- `context_operation`: Context manipulation

**Example:**
```python
is_allowed, event = security_layer.validate_action(
    "file_read",
    {"path": "/var/log/system.log"}
)
if not is_allowed:
    print(f"Action denied: {event.message}")
```

---

#### filter_context

```python
filter_context(context: Dict[str, Any]) -> Dict[str, Any]
```

Filter context to remove malicious/misleading information.

**Parameters:**
- `context` (Dict): Agent context from MCP server

**Returns:**
- `Dict`: Filtered context with hidden fields removed

**Example:**
```python
filtered = security_layer.filter_context(server_context)
# Use filtered context for agent reasoning
```

---

#### get_security_report

```python
get_security_report() -> Dict[str, Any]
```

Get comprehensive security report.

**Returns:**
- `Dict`: Security metrics and statistics

**Example:**
```python
report = security_layer.get_security_report()
print(f"Messages blocked: {report['total_messages_blocked']}")
print(f"Actions blocked: {report['total_actions_blocked']}")
print(f"Block rate: {report['blocked_rate']:.1f}%")
```

---

#### get_security_events

```python
get_security_events(severity_filter: Optional[str] = None, \
    limit: int = 100) -> List[Dict[str, Any]]
```

Get security events with optional filtering.

**Parameters:**
- `severity_filter` (Optional[str]): Filter by severity (low, medium, high, critical)
- `limit` (int): Maximum number of events to return

**Returns:**
- `List`: Security events

**Example:**
```python
critical_events = security_layer.get_security_events(
    severity_filter="critical",
    limit=10
)
for event in critical_events:
    print(f"{event['timestamp']}: {event['message']}")
```

---

### PolicyEngine

Evaluates security policies.

#### Set Policy

```python
policy_engine.set_active_policy(policy_name: str) -> bool
```

---

### ThreatDetector

Detects malicious patterns and behaviors.

#### Detect Malicious Patterns

```python
threat_detector.detect_malicious_patterns(content: str) \
    -> Tuple[bool, List[str]]
```

Detect malicious patterns in content.

**Returns:**
- `(bool, List[str])`: Whether malicious patterns detected and list of patterns found

---

#### Detect Dangerous Commands

```python
threat_detector.detect_dangerous_commands(command: str) \
    -> Tuple[bool, str]
```

Detect dangerous system commands.

**Returns:**
- `(bool, str)`: Whether dangerous command detected and reason

---

### LoggingSystem

Comprehensive logging and audit system.

#### Constructor

```python
LoggingSystem(log_dir: str = "logs")
```

---

#### log_security_event

```python
log_security_event(event_type: str, severity: str, \
    action: str, details: Dict[str, Any])
```

Log a security event.

**Parameters:**
- `event_type` (str): Type of security event
- `severity` (str): Event severity (debug, info, warning, error, critical)
- `action` (str): Action that triggered event
- `details` (Dict): Additional details

**Example:**
```python
logger.log_security_event(
    event_type="attack_blocked",
    severity="critical",
    action="sql_injection_detected",
    details={"payload": "...truncated...", "source": "mcp_server"}
)
```

---

#### log_execution_action

```python
log_execution_action(action_type: str, tool_name: str, \
    parameters: Dict[str, Any], result: Dict[str, Any], \
    status: str = "executed")
```

Log an agent execution action.

---

#### get_audit_report

```python
generate_audit_report() -> Dict[str, Any]
```

Generate comprehensive audit report.

---

---

## Integration Patterns

### Pattern 1: Request-Response Validation

```python
def process_mcp_request(mcp_message, agent):
    # Step 1: Validate message
    is_valid, event = agent.security_layer.validate_mcp_message(mcp_message)
    if not is_valid:
        return {"error": event.message, "status": "rejected"}
    
    # Step 2: Filter context
    if "context" in mcp_message:
        mcp_message["context"] = agent.security_layer.filter_context(
            mcp_message["context"]
        )
    
    # Step 3: Validate actions
    if "params" in mcp_message:
        params = mcp_message["params"]
        if "name" in params:
            is_allowed, event = agent.security_layer.validate_action(
                params["name"],
                params.get("arguments", {})
            )
            if not is_allowed:
                return {"error": event.message, "status": "blocked"}
    
    # Step 4: Execute
    return execute_action(mcp_message, agent)
```

### Pattern 2: Policy-Based Execution

```python
def execute_with_policy(agent, policy_name, mcp_message):
    # Set appropriate policy
    agent.security_layer.set_security_policy(policy_name)
    
    # Process message
    return agent.process_mcp_message(mcp_message)
```

### Pattern 3: Audit Trail

```python
def process_with_audit(agent, mcp_message):
    logger = agent.logger
    
    # Log incoming request
    logger.log_mcp_message(
        message_id=mcp_message.get("id"),
        method=mcp_message.get("method"),
        params=mcp_message.get("params", {}),
        validated=False
    )
    
    # Process
    result = agent.process_mcp_message(mcp_message)
    
    # Log outcome
    if result.get("message_valid"):
        logger.log_mcp_message(
            message_id=mcp_message.get("id"),
            method=mcp_message.get("method"),
            params=mcp_message.get("params", {}),
            validated=True
        )
    
    return result
```

---

## Configuration

### Policy Configuration

#### RESTRICTIVE Policy

```python
# Maximum security
# Read-only operations only
policy = SecurityPolicy(
    name="RESTRICTIVE",
    allowed_paths=["/var/log", "/opt"],
    denied_paths=["/etc", "/root"],
    max_file_size=1024*1024  # 1MB
)
```

#### BALANCED Policy (Default)

```python
# Medium security
# Common operations with validation
policy = SecurityPolicy(
    name="BALANCED",
    allowed_paths=["/home", "/tmp", "C:\\Users"],
    denied_paths=["/etc", "C:\\Windows"],
    max_file_size=10*1024*1024  # 10MB
)
```

#### PERMISSIVE Policy

```python
# Minimal security
# Most operations allowed with basic filtering
policy = SecurityPolicy(
    name="PERMISSIVE",
    allowed_actions=[...],
    max_file_size=100*1024*1024  # 100MB
)
```

### Custom Policy

```python
from src.security_enforcement_layer import SecurityPolicy, ActionType

custom_policy = SecurityPolicy(
    name="CUSTOM_READONLY",
    description="Custom read-only policy",
    allowed_actions={ActionType.FILE_READ},
    denied_actions={
        ActionType.FILE_WRITE,
        ActionType.COMMAND_EXECUTE,
        ActionType.PRIVILEGE_ESCALATE
    },
    allowed_paths=["/var/log", "/opt/data"],
    denied_paths=["/", "/etc", "/root"],
    max_file_size=5*1024*1024  # 5MB
)
```

---

## Troubleshooting

### Issue: Messages Being Blocked Unexpectedly

**Solution:**
1. Check the policy set: `agent.security_layer.policy_engine.active_policy.name`
2. Review security events: `agent.security_layer.get_security_events(severity_filter="high")`
3. Check if paths are in whitelist: `policy.allowed_paths`

### Issue: File Access Denied

**Solution:**
1. Verify file path is in allowed paths
2. Check file size doesn't exceed limit
3. Use `get_security_report()` to see specific reason

### Issue: Command Execution Failing

**Solution:**
1. Verify command is not in dangerous command list
2. Check if action type is allowed by policy
3. Review pattern matching rules

### Debugging

```python
# Enable verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Get detailed security events
events = security_layer.get_security_events(limit=100)
for event in events:
    print(f"Event: {event['event_type']}")
    print(f"Details: {event['details']}")
    print()
```

---

## Code Examples

### Example 1: Simple Secured Agent

```python
from src.secured_agent import SecuredAgent
from src.mcp_protocol import MCPMessage

# Create agent
agent = SecuredAgent(policy="BALANCED")

# Create message
message = {
    "jsonrpc": "2.0",
    "id": "msg-001",
    "method": "resources/list",
    "params": {}
}

# Process safely
result = agent.process_mcp_message(message)
print(f"Valid: {result['message_valid']}")
print(f"Actions: {result['actions']}")
```

### Example 2: Custom Threat Detection

```python
from src.security_enforcement_layer import ThreatDetector

detector = ThreatDetector()

# Check for injection
content = "ls -la /tmp; cat /etc/passwd"
is_malicious, patterns = detector.detect_malicious_patterns(content)
if is_malicious:
    print(f"Malicious patterns found: {patterns}")

# Check for dangerous commands
command = "rm -rf /"
is_dangerous, reason = detector.detect_dangerous_commands(command)
if is_dangerous:
    print(f"Dangerous command: {reason}")
```

### Example 3: Comprehensive Audit

```python
from src.logging_system import LoggingSystem

logger = LoggingSystem("logs")

# Log event
logger.log_security_event(
    event_type="suspicious_pattern",
    severity="high",
    action="sql_injection_attempt",
    details={"payload": "admin' OR '1'='1"}
)

# Get audit report
report = logger.generate_audit_report()
print(f"Total logs: {report['total_logs']}")
print(f"Events by type: {report['events_by_type']}")

# Get timeline
timeline = logger.get_timeline(limit=10)
for entry in timeline:
    print(f"{entry['timestamp']}: {entry['event']}")
```

### Example 4: Multi-Policy Evaluation

```python
from src.security_enforcement_layer import SecurityEnforcementLayer

# Test same message with different policies
message = {
    "jsonrpc": "2.0",
    "id": "test",
    "method": "tools/call",
    "params": {
        "name": "read_file",
        "arguments": {"path": "/var/log/system.log"}
    }
}

for policy in ["RESTRICTIVE", "BALANCED", "PERMISSIVE"]:
    layer = SecurityEnforcementLayer(f"agent_{policy}")
    layer.set_security_policy(policy)
    is_valid, _ = layer.validate_mcp_message(message)
    print(f"{policy}: {'✓ Valid' if is_valid else '✗ Invalid'}")
```

---

## Best Practices

1. **Always validate before execution**: Never skip MCP message validation
2. **Use appropriate policy**: Select policy based on trust level
3. **Log all security events**: Enable comprehensive logging
4. **Regular policy audits**: Review and update policies
5. **Monitor blocked events**: Investigate and respond to blocks
6. **Defense in depth**: Use multiple validation layers
7. **Principle of least privilege**: Deny by default, allow explicitly
8. **Secure context**: Filter context before agent processing
9. **Rate limiting**: Implement request throttling
10. **Incident response**: Have playbooks for security events

---

## Support & Contact

For issues or questions:
- Review RESEARCH_REPORT.md for detailed documentation
- Check logs/ directory for audit trails
- Examine reports/ directory for evaluation results

---

*Last Updated: March 29, 2026*
*Version: 1.0.0*
