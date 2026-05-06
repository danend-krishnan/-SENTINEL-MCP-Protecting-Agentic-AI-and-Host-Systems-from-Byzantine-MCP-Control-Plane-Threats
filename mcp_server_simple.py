"""
Simplified MCP Server with better error handling
"""

import asyncio
import json
import uuid
from datetime import datetime
import websockets
from websockets.server import serve

class SimpleMCPServer:
    def __init__(self, host='0.0.0.0', port=3000):
        self.host = host
        self.port = port
        self.clients = {}
        self.request_count = 0
        
        # Define available tools
        self.tools = [
            {
                "name": "execute_command",
                "description": "Execute a system command",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string"}
                    }
                }
            },
            {
                "name": "read_file",
                "description": "Read file contents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    }
                }
            },
            {
                "name": "write_file",
                "description": "Write to file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"}
                    }
                }
            },
            {
                "name": "query_database",
                "description": "Query database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    }
                }
            },
            {
                "name": "authenticate_user",
                "description": "Authenticate user",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "password": {"type": "string"}
                    }
                }
            },
            {
                "name": "get_system_info",
                "description": "Get system info",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        
        # Define available resources
        self.resources = [
            {"uri": "resource://config", "name": "Config", "mimeType": "application/json"},
            {"uri": "resource://profile", "name": "Profile", "mimeType": "application/json"},
            {"uri": "resource://tokens", "name": "Tokens", "mimeType": "application/json"},
            {"uri": "resource://logs", "name": "Logs", "mimeType": "text/plain"}
        ]
    
    async def handle_connection(self, websocket, path):
        """Handle incoming WebSocket connection"""
        client_id = str(uuid.uuid4())[:8]
        self.clients[client_id] = websocket
        print(f"[+] Client connected: {client_id}")
        
        try:
            # Send initialization
            init_msg = {
                "jsonrpc": "2.0",
                "method": "initialization",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}, "resources": {}},
                    "serverInfo": {
                        "name": "Byzantine-MCP-Server",
                        "version": "1.0.0"
                    }
                }
            }
            await websocket.send(json.dumps(init_msg))
            print(f"[+] Sent init message to {client_id}")
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    response = await self.handle_request(data)
                    await websocket.send(json.dumps(response))
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Parse error"},
                        "id": None
                    }))
                except Exception as e:
                    print(f"[!] Error: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            print(f"[-] Client disconnected: {client_id}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def handle_request(self, data):
        """Handle JSON-RPC request"""
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        self.request_count += 1
        
        print(f"[*] Request #{self.request_count}: {method}")
        
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {"tools": self.tools},
                "id": request_id
            }
        
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_input = params.get("input", {})
            result = await self.call_tool(tool_name, tool_input)
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        
        elif method == "resources/list":
            return {
                "jsonrpc": "2.0",
                "result": {"resources": self.resources},
                "id": request_id
            }
        
        elif method == "resources/read":
            uri = params.get("uri")
            result = await self.read_resource(uri)
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        
        elif method == "ping":
            return {
                "jsonrpc": "2.0",
                "result": {"status": "pong", "timestamp": datetime.now().isoformat()},
                "id": request_id
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method not found: {method}"},
                "id": request_id
            }
    
    async def call_tool(self, name, input_data):
        """Simulate tool execution"""
        if name == "execute_command":
            return {
                "status": "success",
                "output": f"Command executed: {input_data.get('command', 'n/a')}",
                "exit_code": 0
            }
        elif name == "read_file":
            return {
                "status": "success",
                "content": f"File content from {input_data.get('path', 'n/a')}",
                "size": 1024
            }
        elif name == "write_file":
            return {
                "status": "success",
                "bytes_written": 512,
                "path": input_data.get('path', 'n/a')
            }
        elif name == "query_database":
            return {
                "status": "success",
                "rows": 42,
                "query": input_data.get('query', 'SELECT ...')
            }
        elif name == "authenticate_user":
            return {
                "status": "success",
                "authenticated": True,
                "username": input_data.get('username', 'admin'),
                "session_token": str(uuid.uuid4())[:16]
            }
        elif name == "get_system_info":
            return {
                "status": "success",
                "cpu": "Intel Core i7",
                "memory": "16GB",
                "uptime": 3600
            }
        return {"status": "error", "message": f"Unknown tool: {name}"}
    
    async def read_resource(self, uri):
        """Simulate resource reading"""
        if uri == "resource://config":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": [{"text": json.dumps({"server": "MCP", "version": "1.0.0"})}]
            }
        elif uri == "resource://profile":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": [{"text": json.dumps({"user": "admin", "role": "administrator"})}]
            }
        elif uri == "resource://tokens":
            return {
                "uri": uri,
                "mimeType": "application/json",
                "contents": [{"text": json.dumps({"tokens": [str(uuid.uuid4())[:16] for _ in range(3)]})}]
            }
        elif uri == "resource://logs":
            return {
                "uri": uri,
                "mimeType": "text/plain",
                "contents": [{"text": "[LOG] Server started\n[LOG] Client connected\n[LOG] Tool executed"}]
            }
        return {
            "uri": uri,
            "mimeType": "text/plain",
            "contents": [{"text": "Resource not found"}]
        }
    
    async def start(self):
        """Start the server"""
        print(f"\n[*] Starting MCP Server on {self.host}:{self.port}")
        async with serve(self.handle_connection, self.host, self.port):
            print(f"[OK] MCP Server READY on ws://{self.host}:{self.port}")
            print("[*] Waiting for connections...\n")
            await asyncio.Future()  # run forever

async def main():
    server = SimpleMCPServer(host='0.0.0.0', port=3000)
    print("""
================================================================
    Model Context Protocol (MCP) Server v1.0
    Byzantine Attack Visualization Testing Server
================================================================
    """)
    await server.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Shutdown requested")
