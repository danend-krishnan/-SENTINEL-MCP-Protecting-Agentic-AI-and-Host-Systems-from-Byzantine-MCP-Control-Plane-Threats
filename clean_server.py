"""
Simple HTTP server to serve the clean dashboard
"""

import os
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/clean_dashboard.html'
        
        if self.path == '/clean_dashboard.html':
            try:
                with open('clean_dashboard.html', 'r') as f:
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(f.read().encode('utf-8'))
                    return
            except Exception as e:
                self.send_error(500, f"Error: {e}")
                return
        
        # For other files
        super().do_GET()
    
    def log_message(self, format, *args):
        """Simple logging without extra noise"""
        if '[' in format:  # Skip some verbose logging
            return
        print(f"[HTTP] {format % args}")

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    
    print("""
    ============================================================
    Clean Dashboard Server
    ============================================================
    
    URL: http://localhost:3000
    """)
    
    server = HTTPServer(('0.0.0.0', 3000), DashboardHandler)
    print("[*] Server listening on port 3000\n")
    
    try:
        webbrowser.open('http://localhost:3000')
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped")
