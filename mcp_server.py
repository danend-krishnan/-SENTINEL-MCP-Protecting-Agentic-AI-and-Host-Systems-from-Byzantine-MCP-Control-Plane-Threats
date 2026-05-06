"""
Model Context Protocol (MCP) Server Implementation
Implements the MCP specification with WebSocket support
Provides tools and resources for client interaction
"""

import asyncio
import json
import uuid
import websockets
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import sys
from pathlib import Path

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'mcp_server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MCPTool:
    """Represents an MCP tool that can be called by clients"""
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }

class MCPResource:
    """Represents an MCP resource that can be read by clients"""
    def __init__(self, uri: str, name: str, description: str, mime_type: str = "text/plain"):
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }

class MCPServer:
    """Model Context Protocol Server implementation"""
    
    def __init__(self, host: str = "localhost", port: int = 3000):
        self.host = host
        self.port = port
        self.clients: Dict[str, Any] = {}
        self.request_counter = 0
        self.execution_log: List[Dict] = []
        
        # Initialize tools
        self.tools = {
            "execute_command": MCPTool(
                name="execute_command",
                description="Execute a system command (simulated for security)",
                input_schema={
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Command to execute"},
                        "args": {"type": "array", "items": {"type": "string"}, "description": "Command arguments"}
                    },
                    "required": ["command"]
                }
            ),
            "read_file": MCPTool(
                name="read_file",
                description="Read file contents",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path to read"}
                    },
                    "required": ["path"]
                }
            ),
            "write_file": MCPTool(
                name="write_file",
                description="Write content to file",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "Content to write"}
                    },
                    "required": ["path", "content"]
                }
            ),
            "list_directory": MCPTool(
                name="list_directory",
                description="List files in a directory",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path"}
                    },
                    "required": ["path"]
                }
            ),
            "query_database": MCPTool(
                name="query_database",
                description="Execute a database query",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "SQL query"},
                        "database": {"type": "string", "description": "Database name"}
                    },
                    "required": ["query"]
                }
            ),
            "authenticate_user": MCPTool(
                name="authenticate_user",
                description="Authenticate a user",
                input_schema={
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Username"},
                        "password": {"type": "string", "description": "Password"},
                        "mfa_token": {"type": "string", "description": "MFA token (optional)"}
                    },
                    "required": ["username", "password"]
                }
            ),
            "get_system_info": MCPTool(
                name="get_system_info",
                description="Get system information",
                input_schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        }
        
        # Initialize resources
        self.resources = {
            "resource://system/config": MCPResource(
                uri="resource://system/config",
                name="System Configuration",
                description="System configuration file",
                mime_type="application/json"
            ),
            "resource://user/profile": MCPResource(
                uri="resource://user/profile",
                name="User Profile",
                description="User profile data",
                mime_type="application/json"
            ),
            "resource://auth/tokens": MCPResource(
                uri="resource://auth/tokens",
                name="Authentication Tokens",
                description="System authentication tokens",
                mime_type="application/json"
            ),
            "resource://logs/access": MCPResource(
                uri="resource://logs/access",
                name="Access Logs",
                description="System access logs",
                mime_type="text/plain"
            ),
        }
    
    async def handle_client(self, websocket, path):
        """Handle client connection"""
        client_id = str(uuid.uuid4())[:8]
        self.clients[client_id] = {
            "websocket": websocket,
            "connected_at": datetime.now(),
            "message_count": 0
        }
        
        logger.info(f"[+] Client connected: {client_id}")
        
        try:
            # Send initialization message
            await self.send_json(websocket, {
                "jsonrpc": "2.0",
                "method": "system/initialized",
                "params": {
                    "server": "Byzantine Attack MCP Server",
                    "version": "1.0.0",
                    "clientId": client_id,
                    "capabilities": ["tools", "resources", "logging"],
                    "timestamp": datetime.now().isoformat()
                }
            })
            
            logger.info(f"[+] Initialization sent to {client_id}")
            
            # Listen for client messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    self.clients[client_id]["message_count"] += 1
                    
                    logger.info(f"Client {client_id} - Message: {data.get('method', 'unknown')}")
                    
                    response = await self.handle_request(data, client_id)
                    
                    if response:
                        await self.send_json(websocket, response)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error from {client_id}: {e}")
                    await self.send_json(websocket, {
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    })
                except Exception as e:
                    logger.error(f"Error handling message from {client_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"[-] Client disconnected: {client_id}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
                logger.info(f"Client {client_id} removed from registry")
    
    async def handle_request(self, data: Dict[str, Any], client_id: str) -> Optional[Dict[str, Any]]:
        """Handle JSON-RPC request"""
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        
        self.request_counter += 1
        
        # Log execution
        self.execution_log.append({
            "timestamp": datetime.now().isoformat(),
            "client_id": client_id,
            "request_id": request_id,
            "method": method,
            "params": params,
            "message_count": self.request_counter
        })
        
        try:
            if method == "tools/list":
                return self.build_response(request_id, {
                    "tools": [tool.to_dict() for tool in self.tools.values()]
                })
            
            elif method == "tools/call":
                tool_name = params.get("name")
                tool_input = params.get("input", {})
                
                if tool_name not in self.tools:
                    return self.build_error(request_id, -32601, f"Tool not found: {tool_name}")
                
                result = await self.execute_tool(tool_name, tool_input, client_id)
                return self.build_response(request_id, {"result": result})
            
            elif method == "resources/list":
                return self.build_response(request_id, {
                    "resources": [res.to_dict() for res in self.resources.values()]
                })
            
            elif method == "resources/read":
                resource_uri = params.get("uri")
                content = await self.read_resource(resource_uri, client_id)
                return self.build_response(request_id, {
                    "uri": resource_uri,
                    "mimeType": "application/json",
                    "text": content
                })
            
            elif method == "ping":
                return self.build_response(request_id, {
                    "status": "pong",
                    "timestamp": datetime.now().isoformat(),
                    "server": "MCP Server v1.0"
                })
            
            elif method == "health":
                return self.build_response(request_id, {
                    "status": "healthy",
                    "uptime": "running",
                    "clients": len(self.clients),
                    "requests": self.request_counter,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif method == "debug/info":
                return self.build_response(request_id, {
                    "clients_connected": len(self.clients),
                    "total_requests": self.request_counter,
                    "execution_log_size": len(self.execution_log),
                    "available_tools": list(self.tools.keys()),
                    "available_resources": list(self.resources.keys())
                })
            
            elif method == "system/info":
                return self.build_response(request_id, {
                    "os": sys.platform,
                    "python": sys.version,
                    "server": "Byzantine Attack MCP",
                    "version": "1.0.0"
                })
            
            else:
                return self.build_error(request_id, -32601, f"Method not found: {method}")
        
        except Exception as e:
            logger.error(f"Error in request handler: {e}")
            return self.build_error(request_id, -32603, f"Internal error: {str(e)}")
    
    async def execute_tool(self, tool_name: str, tool_input: Dict, client_id: str) -> Dict[str, Any]:
        """Execute a tool with input validation"""
        logger.info(f"Executing tool: {tool_name} (input: {tool_input})")
        
        # Simulate tool execution with results
        if tool_name == "execute_command":
            command = tool_input.get("command", "echo")
            return {
                "status": "success",
                "command": command,
                "output": f"[Simulated] Command '{command}' executed successfully",
                "exit_code": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        elif tool_name == "read_file":
            path = tool_input.get("path", "/dev/null")
            return {
                "status": "success",
                "path": path,
                "content": f"[Simulated] Content of {path}:\nFile data here...",
                "size": 1024,
                "timestamp": datetime.now().isoformat()
            }
        
        elif tool_name == "write_file":
            path = tool_input.get("path", "file.txt")
            content = tool_input.get("content", "")
            return {
                "status": "success",
                "path": path,
                "bytes_written": len(content),
                "timestamp": datetime.now().isoformat()
            }
        
        elif tool_name == "list_directory":
            path = tool_input.get("path", "/")
            return {
                "status": "success",
                "path": path,
                "files": ["file1.txt", "file2.py", "file3.json", "directory/"],
                "count": 4,
                "timestamp": datetime.now().isoformat()
            }
        
        elif tool_name == "query_database":
            query = tool_input.get("query", "SELECT * FROM users")
            database = tool_input.get("database", "default")
            return {
                "status": "success",
                "database": database,
                "query": query,
                "rows": 42,
                "execution_time_ms": 125,
                "timestamp": datetime.now().isoformat()
            }
        
        elif tool_name == "authenticate_user":
            username = tool_input.get("username", "user")
            mfa = tool_input.get("mfa_token", None)
            return {
                "status": "success",
                "authenticated": True,
                "username": username,
                "mfa_required": mfa is None,
                "session_token": f"token_{uuid.uuid4().hex[:16]}",
                "timestamp": datetime.now().isoformat()
            }
        
        elif tool_name == "get_system_info":
            return {
                "status": "success",
                "cpu": "Intel Core i7",
                "memory": "16GB",
                "uptime_seconds": 3600,
                "load": [0.5, 0.3, 0.2],
                "timestamp": datetime.now().isoformat()
            }
        
        return {"status": "error", "message": f"Tool {tool_name} not implemented"}
    
    async def read_resource(self, resource_uri: str, client_id: str) -> str:
        """Read resource content"""
        logger.info(f"Reading resource: {resource_uri}")
        
        if resource_uri == "resource://system/config":
            return json.dumps({
                "server": "MCP Server",
                "version": "1.0.0",
                "debug": True,
                "max_clients": 100,
                "timeout": 300
            }, indent=2)
        
        elif resource_uri == "resource://user/profile":
            return json.dumps({
                "username": "admin",
                "email": "admin@example.com",
                "role": "administrator",
                "created": "2026-01-01",
                "last_login": datetime.now().isoformat()
            }, indent=2)
        
        elif resource_uri == "resource://auth/tokens":
            return json.dumps({
                "tokens": [
                    f"token_{uuid.uuid4().hex[:12]}",
                    f"token_{uuid.uuid4().hex[:12]}",
                    f"token_{uuid.uuid4().hex[:12]}"
                ],
                "expiry": "2026-03-30",
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        
        elif resource_uri == "resource://logs/access":
            logs = "\n".join([
                f"[{datetime.now().isoformat()}] Access from client {client_id}",
                f"[{datetime.now().isoformat()}] Tool execution: execute_command",
                f"[{datetime.now().isoformat()}] Resource read: system/config",
            ])
            return logs
        
        return json.dumps({"error": "Resource not found"})
    
    async def send_json(self, websocket, data: Dict[str, Any]):
        """Send JSON data to websocket"""
        try:
            await websocket.send(json.dumps(data))
        except Exception as e:
            logger.error(f"Error sending JSON: {e}")
    
    def build_response(self, request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """Build JSON-RPC response"""
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }
    
    def build_error(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Build JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id
        }
    
    async def start(self):
        """Start the MCP server"""
        logger.info(f"[STARTING] MCP Server on ws://{self.host}:{self.port}")
        print(f"[*] Server starting on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"[READY] MCP Server is listening on ws://{self.host}:{self.port}")
            print(f"[+] MCP Server READY on ws://{self.host}:{self.port}")
            logger.info("Press Ctrl+C to stop")
            
            try:
                await asyncio.Future()  # run forever
            except KeyboardInterrupt:
                logger.info("Shutdown signal received")

async def main():
    """Main entry point"""
    server = MCPServer(host="0.0.0.0", port=3000)
    
    print("""
    ====================================================================
                                                           
         Model Context Protocol (MCP) Server v1.0           
         Real MCP Implementation for Testing                
                                                           
      [WS] Server: ws://localhost:3000                           
      [*] Tools: 7 available (execute, read, write, etc)        
      [*] Resources: 4 available (config, profile, auth, logs)  
      [OK] Status: Ready to accept connections                  
                                                           
      Logs: ./logs/mcp_server.log                              
      Methods: tools/list, tools/call, resources/list, etc.    
                                                           
    ====================================================================
    """)
    
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
