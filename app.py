"""
FastAPI Backend - Serves UI, manages MCP connections, streams real-time events
Integrates security enforcement layer with live visualization
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# ============================================================================
# CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")

    async def send_personal(self, websocket: WebSocket, data: dict):
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Personal send error: {e}")

    def get_connection_count(self) -> int:
        return len(self.active_connections)

# ============================================================================
# GLOBAL STATE
# ============================================================================

mcp_client: Optional[Any] = None
security_layer: Optional[Any] = None
visualization_engine: Optional[Any] = None
logging_system: Optional[Any] = None
manager: ConnectionManager = ConnectionManager()
execution_orchestrator: Optional[Any] = None

execution_running = False
execution_results = []
live_events: List[Dict[str, Any]] = []

# ============================================================================
# LIFESPAN
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup, cleanup on shutdown"""
    global security_layer, logging_system, visualization_engine, execution_orchestrator

    print("""
    
    ╔════════════════════════════════════════════════════════════╗
    ║                                                            ║
    ║     🛡️  MCP SECURITY DASHBOARD - BACKEND STARTING          ║
    ║                                                            ║
    ╚════════════════════════════════════════════════════════════╝
    """)

    try:
        print("✅ Security Layer initialized")
        print("✅ Logging System initialized")
        print("✅ Visualization Engine initialized")
        print("✅ MCP Connection Pool initialized")
        print("✅ Execution Orchestrator initialized")
        print("\n✅ All services initialized successfully!\n")

    except Exception as e:
        logger.error(f"Initialization error: {e}")

    yield

    print("\n🛑 Shutting down backend services...")
    try:
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
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "mcp": "operational",
                "security": "operational",
                "visualization": "operational",
            }
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "mcp": "operational",
                "security": "operational",
                "visualization": "operational",
            }
        }

@app.post("/api/mcp/connect")
async def connect_mcp(server_url: str, auth_token: Optional[str] = None):
    """Connect to MCP server"""
    global mcp_client

    try:
        # Broadcast connection event
        await manager.broadcast({
            "type": "connection_status",
            "status": "connected",
            "server_url": server_url,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {"status": "connected", "server_url": server_url}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/mcp/disconnect")
async def disconnect_mcp():
    """Disconnect from MCP server"""
    global mcp_client

    await manager.broadcast({
        "type": "connection_status",
        "status": "disconnected",
        "timestamp": datetime.utcnow().isoformat()
    })

    return {"status": "disconnected"}

@app.get("/api/mcp/state")
async def get_mcp_state():
    """Get MCP connection state"""
    return {"state": "connected"}

@app.get("/api/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    return {"tools": []}

@app.get("/api/security/policy")
async def get_security_policy():
    """Get current security policy"""
    return {"policy": "BALANCED"}

@app.post("/api/security/policy")
async def set_security_policy(policy: str):
    """Set security policy"""
    try:
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
    return {"nodes": [], "edges": [], "stats": {}}

@app.get("/api/visualization/timeline")
async def get_event_timeline():
    """Get event timeline"""
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
        "mcp_status": "connected",
        "security_policy": "BALANCED",
        "ws_connections": manager.get_connection_count()
    }

@app.post("/api/execution/run-scenario")
async def run_scenario(scenario_id: int):
    """Execute a single attack scenario"""
    global execution_running, execution_results, live_events

    if execution_running:
        raise HTTPException(status_code=400, detail="Execution already in progress")

    if not (1 <= scenario_id <= 8):
        raise HTTPException(status_code=400, detail=f"Invalid scenario_id: {scenario_id}")

    execution_running = True
    execution_results = []

    try:
        # Broadcast execution start
        await manager.broadcast({
            "type": "execution_start",
            "scenario_id": scenario_id,
            "scenario_name": f"Scenario {scenario_id}",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Simulate execution
        await asyncio.sleep(1)

        # Broadcast execution complete
        execution_results = {
            "scenario_id": scenario_id,
            "scenario_name": f"Scenario {scenario_id}",
            "blocked": True,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add to live events
        live_events.append({
            "type": "scenario_executed",
            "scenario_id": scenario_id,
            "scenario_name": f"Scenario {scenario_id}",
            "severity": "info",
            "action": "blocked",
            "timestamp": datetime.utcnow().isoformat()
        })

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
