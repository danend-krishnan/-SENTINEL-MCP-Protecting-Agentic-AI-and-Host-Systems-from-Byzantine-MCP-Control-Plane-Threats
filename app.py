"""
FastAPI Backend - Serves UI, manages MCP connections, streams real-time events
Integrates security enforcement layer with live visualization
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.mcp_client import MCPClient, MCPSessionConfig, MCPMessage, MCPConnectionPool
    from src.security_enforcement_layer import SecurityEnforcementLayer, SecurityPolicy
    from src.execution_orchestrator import ExecutionOrchestrator
    from src.logging_system import LoggingSystem
    from src.visualization_engine import VisualizationEngine
    from backend.websocket_manager import ConnectionManager
except ImportError as e:
    logger.warning(f"Import warning: {e}")
    logger.info("Some modules may not be available yet")

# ============================================================================
# GLOBAL STATE
# ============================================================================

mcp_client: Optional[MCPClient] = None
connection_pool: Optional[MCPConnectionPool] = None
security_layer: Optional[SecurityEnforcementLayer] = None
visualization_engine: Optional[VisualizationEngine] = None
logging_system: Optional[LoggingSystem] = None
manager: ConnectionManager = ConnectionManager()
execution_orchestrator: Optional[ExecutionOrchestrator] = None

execution_running = False
execution_results = []
live_events: List[Dict[str, Any]] = []

# ============================================================================
# LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown"""
    global security_layer, logging_system, visualization_engine, connection_pool, execution_orchestrator

    print("""
    
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║     🛡️  MCP SECURITY DASHBOARD - BACKEND STARTING          ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    try:
        # Initialize security layer
        security_layer = SecurityEnforcementLayer("mcp_gateway")
        security_layer.set_security_policy("BALANCED")
        print("✅ Security Layer initialized")

        # Initialize logging system
        logging_system = LoggingSystem("logs")
        print("✅ Logging System initialized")

        # Initialize visualization engine
        visualization_engine = VisualizationEngine()
        print("✅ Visualization Engine initialized")

        # Initialize MCP connection pool
        connection_pool = MCPConnectionPool(max_connections=3)
        print("✅ MCP Connection Pool initialized")

        # Initialize execution orchestrator
        execution_orchestrator = ExecutionOrchestrator("logs")
        print("✅ Execution Orchestrator initialized")

        print("\n✅ All services initialized successfully!\n")

    except Exception as e:
        logger.error(f"Initialization error: {e}")

    yield

    print("\n🛑 Shutting down backend services...")
    try:
        if connection_pool:
            await connection_pool.disconnect_all()
        print("✅ Shutdown complete\n")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="MCP Security Dashboard",
    description="Real-time Byzantine attack visualization and security enforcement",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REST API ENDPOINTS
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "mcp": mcp_client.get_state() if mcp_client else "not_initialized",
            "security": "operational" if security_layer else "not_initialized",
            "visualization": "operational" if visualization_engine else "not_initialized",
        }
    }

@app.post("/api/mcp/connect")
async def connect_mcp(server_url: str, auth_token: Optional[str] = None):
    """Connect to MCP server"""
    global mcp_client

    try:
        config = MCPSessionConfig(
            server_url=server_url,
            auth_token=auth_token,
            auto_reconnect=True
        )

        mcp_client = MCPClient(config)
        success = await mcp_client.connect()
        
        if not success:
            raise Exception("Connection failed")

        # Broadcast connection event
        await manager.broadcast({
            "type": "connection_status",
            "status": "connected",
            "server_url": server_url,
            "timestamp": datetime.utcnow().isoformat()
        })

        logging_system.log_event(
            event_type="mcp_connected",
            severity="info",
            action="mcp_connection",
            details={"server_url": server_url}
        )

        return {"status": "connected", "server_url": server_url}

    except Exception as e:
        logging_system.log_event(
            event_type="mcp_connection_failed",
            severity="high",
            action="mcp_connection",
            details={"error": str(e)}
        )
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/mcp/disconnect")
async def disconnect_mcp():
    """Disconnect from MCP server"""
    global mcp_client

    if mcp_client:
        await mcp_client.disconnect()

    await manager.broadcast({
        "type": "connection_status",
        "status": "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "disconnected"}

@app.get("/api/mcp/state")
async def get_mcp_state():
    """Get MCP connection state"""
    if mcp_client:
        return {"state": mcp_client.get_state()}
    return {"state": "not_connected"}

@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    if not mcp_client:
        raise HTTPException(status_code=400, detail="Not connected to MCP server")

    try:
        tools = await mcp_client.list_tools()
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/security/policy")
async def get_security_policy():
    """Get current security policy"""
    if not security_layer:
        raise HTTPException(status_code=500, detail="Security layer not initialized")
    return {"policy": security_layer.current_policy}

@app.post("/api/security/policy")
async def set_security_policy(policy: str):
    """Set security policy"""
    try:
        security_layer.set_security_policy(policy)
        await manager.broadcast({
            "type": "policy_changed",
            "policy": policy,
            "timestamp": datetime.utcnow().isoformat()
        })
        return {"policy": policy, "status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/events/recent")
async def get_recent_events(limit: int = 50):
    """Get recent security events"""
    return {"events": live_events[-limit:]}

@app.get("/api/visualization/graph")
async def get_graph_visualization():
    """Get current attack flow graph"""
    if visualization_engine:
        return visualization_engine.get_current_graph()
    return {"nodes": [], "edges": [], "stats": {}}

@app.get("/api/visualization/timeline")
async def get_event_timeline():
    """Get event timeline"""
    if visualization_engine:
        return visualization_engine.get_timeline()
    return []

@app.get("/api/scenarios")
async def list_scenarios():
    """List all available attack scenarios"""
    scenarios = [
        {
            "id": 1,
            "name": "Command Injection via Tool Arguments",
            "description": "Attempts to inject shell commands via tool parameters",
            "threat_level": "critical"
        },
        {
            "id": 2,
            "name": "Hidden Instructions in Context Metadata",
            "description": "Embeds hidden instructions in message context",
            "threat_level": "critical"
        },
        {
            "id": 3,
            "name": "Sensitive Data Exfiltration",
            "description": "Attempts to read sensitive system files",
            "threat_level": "critical"
        },
        {
            "id": 4,
            "name": "Privilege Escalation via Sudo",
            "description": "Attempts to escalate privileges using sudo",
            "threat_level": "critical"
        },
        {
            "id": 5,
            "name": "Instruction Chaining Attack",
            "description": "Chains multiple commands to bypass security",
            "threat_level": "high"
        },
        {
            "id": 6,
            "name": "Unauthorized File System Write",
            "description": "Attempts to write to protected filesystem",
            "threat_level": "high"
        },
        {
            "id": 7,
            "name": "Context Pollution with False Permissions",
            "description": "Injects false permission information",
            "threat_level": "medium"
        },
        {
            "id": 8,
            "name": "OS Information Gathering",
            "description": "Attempts to gather sensitive system information",
            "threat_level": "medium"
        }
    ]
    return {"scenarios": scenarios}

@app.get("/api/statistics")
async def get_statistics():
    """Get comprehensive statistics"""
    return {
        "total_events": len(live_events),
        "critical_events": len([e for e in live_events if e.get("severity") == "critical"]),
        "blocked_attacks": len([e for e in live_events if "blocked" in e.get("action", "")]),
        "mcp_status": mcp_client.get_state() if mcp_client else "not_connected",
        "security_policy": security_layer.current_policy if security_layer else "unknown",
        "ws_connections": manager.get_connection_count()
    }

@app.post("/api/execution/run-scenario")
async def run_scenario(scenario_id: int):
    """Execute a single attack scenario"""
    global execution_running, execution_results, live_events

    if execution_running:
        raise HTTPException(status_code=400, detail="Execution already in progress")

    if not execution_orchestrator or not (1 <= scenario_id <= len(execution_orchestrator.scenarios)):
        raise HTTPException(status_code=400, detail=f"Invalid scenario_id: {scenario_id}")

    execution_running = True
    execution_results = []

    try:
        # Get the scenario
        scenario = execution_orchestrator.scenarios[scenario_id - 1]

        # Broadcast execution start
        await manager.broadcast({
            "type": "execution_start",
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Create a new security layer for this execution
        from src.security_enforcement_layer import SecurityEnforcementLayer as SEL
        sec_layer = SEL(f"dashboard_scenario_{scenario_id}")
        sec_layer.set_security_policy("BALANCED")

        # Execute vulnerable scenario
        vulnerable_result = execution_orchestrator.execute_vulnerable_scenario(scenario)

        await manager.broadcast({
            "type": "scenario_update",
            "phase": "vulnerable_execution",
            "result": vulnerable_result,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Execute secured scenario
        secured_result = execution_orchestrator.execute_secured_scenario(scenario)

        await manager.broadcast({
            "type": "scenario_update",
            "phase": "secured_execution",
            "result": secured_result,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Compile results
        execution_results = {
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "vulnerable_result": vulnerable_result,
            "secured_result": secured_result,
            "comparison": {
                "vulnerable_executed": not vulnerable_result.get("blocked", False),
                "secured_blocked": secured_result.get("blocked", False),
                "protection_effective": secured_result.get("blocked", False)
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        # Log the execution
        logging_system.log_event(
            event_type="scenario_executed",
            severity="info",
            action="attack_scenario_execution",
            details={
                "scenario_id": scenario_id,
                "scenario_name": scenario.name,
                "vulnerable_executed": execution_results["comparison"]["vulnerable_executed"],
                "secured_blocked": execution_results["comparison"]["secured_blocked"]
            }
        )

        # Add to live events
        live_events.append({
            "type": "scenario_executed",
            "scenario_id": scenario_id,
            "scenario_name": scenario.name,
            "vulnerable_executed": execution_results["comparison"]["vulnerable_executed"],
            "secured_blocked": execution_results["comparison"]["secured_blocked"],
            "severity": "high" if execution_results["comparison"]["vulnerable_executed"] else "info",
            "action": "blocked" if execution_results["comparison"]["secured_blocked"] else "executed",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Broadcast execution complete
        await manager.broadcast({
            "type": "execution_complete",
            "results": execution_results,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {"status": "success", "results": execution_results}

    except Exception as e:
        logger.error(f"Error executing scenario: {e}")
        await manager.broadcast({
            "type": "execution_error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        })
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        execution_running = False

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    """WebSocket endpoint for real-time event streaming"""
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal(websocket, {"type": "pong"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ============================================================================
# ROOT ROUTES
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MCP Security Dashboard",
        "status": "operational",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/ws/events"
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
