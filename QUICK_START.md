# 🚀 QUICK START - MCP SECURITY DASHBOARD

## ⚡ 5-MINUTE SETUP

### Prerequisites Check

```powershell
# Check Python
python --version  # Should show 3.14+

# Check Node.js (if not installed, see "Install Node.js" below)
node --version
npm --version
```

### STEP 1: Install Backend Dependencies

```powershell
cd backend
pip install -r requirements.txt
cd ..
```

Expected output:
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 websockets-12.0 ...
```

### STEP 2: Install Frontend Dependencies

**Windows Users:**

Option A - If npm is installed:
```powershell
cd frontend
npm install
cd ..
```

Option B - If npm is NOT installed:
- Download Node.js from https://nodejs.org/ (LTS version)
- Install it
- Then run the commands above

**Linux/Mac:**
```bash
cd frontend
npm install
cd ..
```

### STEP 3: Start the Backend

**Windows:**
```powershell
cd backend
.\start.bat
```

**Linux/Mac:**
```bash
cd backend
bash start.sh
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### STEP 4: Start the Frontend (New Terminal)

**Windows:**
```powershell
cd frontend
.\start.bat
```

**Linux/Mac:**
```bash
cd frontend
bash start.sh
```

You should see:
```
Compiled successfully!
To create a production build, use npm run build.
```

### STEP 5: Open Dashboard

Open your browser and go to:
```
http://localhost:3000
```

You should see the **MCP Security Dashboard** with:
- ✅ Green "WebSocket: Connected"
- Left panel with connection controls
- Center graph area
- Right panel with events timeline

---

## 🎯 Basic Usage (First Time)

### 1. Connect to MCP Server

In the left panel "MCP Connection":
- Enter URL: `ws://localhost:3000` (or your MCP server URL)
- Leave auth token empty (or add if required)
- Click **Connect** button
- Wait for ✓ Connected status

### 2. Run First Attack Scenario

In "Execute Scenarios":
- Keep default selection: **1: Command Injection**
- Click **Run Scenario** button
- Watch output in console area

### 3. Observe Results

The center graph will show:
- 🔴 Red nodes: Malicious MCP server
- 🟡 Orange nodes: Attack payloads
- 🟢 Green nodes: Blocked/Allowed results
- 🔵 Blue nodes: Security layer checks

The right timeline will show:
- When attack occurred
- Whether it was blocked
- Reason for decision

---

## 📊 Exploring All 8 Scenarios

```
1. Command Injection via Tool Arguments       [Critical]
2. Hidden Instructions in Context Metadata    [Critical]
3. Sensitive Data Exfiltration                [Critical]
4. Privilege Escalation via Sudo              [Critical]
5. Instruction Chaining Attack                [High]
6. Unauthorized File System Write             [High]
7. Context Pollution with False Permissions   [Medium]
8. OS Information Gathering                   [Medium]
```

Try each one to see different attack patterns!

---

## 🔧 Configuration (Optional)

### Change MCP Server URL

If your MCP server is running on different host/port:

**In Dashboard:**
1. Disconnect (if connected)
2. Enter new URL in MCP Connection panel
3. Reconnect

### Change Security Policy

**In Dashboard:**
1. Select from dropdown (if available in future versions)
2. Policy options:
   - **RESTRICTIVE**: Maximum protection (blocks more)
   - **BALANCED**: Default (good balance)
   - **PERMISSIVE**: Minimal restrictions (allows more)

---

## ✅ Verification Checklist

After startup, verify:

```
Backend Status:
  ✓ Terminal shows "Uvicorn running on..."
  ✓ API available at http://localhost:8000/docs
  ✓ No error messages in backend terminal

Frontend Status:
  ✓ Terminal shows "Compiled successfully!"
  ✓ Frontend at http://localhost:3000
  ✓ Dashboard visible in browser

Dashboard Status:
  ✓ WebSocket: Connected (green)
  ✓ Left panel visible
  ✓ Center graph area visible
  ✓ Right timeline visible
  ✓ No console errors (F12 to check)
```

---

## 🐛 Troubleshooting

### "Cannot GET /" on localhost:3000

**Solution:** Frontend still building. Wait 30 seconds and refresh.

### "WebSocket: Disconnected" (red)

**Solution:** Check backend is running:
```powershell
curl http://localhost:8000/api/health
```

Should return JSON with status.

### Port 8000 or 3000 already in use

**Windows:**
```powershell
# Find process
netstat -ano | findstr :8000

# Kill process  
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# Find process
lsof -i :8000

# Kill process
kill <PID>
```

### "npm: The term is not recognized"

**Solution:** Install Node.js from https://nodejs.org/

### Python module not found errors

**Solution:**
```powershell
# Reinstall dependencies
pip install -r backend/requirements.txt
```

---

## 📚 Next Steps

### 1. Read Documentation
- **UI_GUIDE.md** - Complete dashboard guide
- **DEPLOYMENT_GUIDE.md** - Production deployment
- **RESEARCH_REPORT.md** - Technical details

### 2. Run Security Tests
```powershell
# From project root
python main.py
```

This runs the standalone test suite and generates reports in `reports/` directory.

### 3. Connect Real MCP Server
Once comfortable with test scenarios, connect your actual MCP server:
1. Get WebSocket URL of your MCP server
2. Enter in dashboard
3. Run real attack scenarios

### 4. Monitor Logs
```powershell
# View security events
Get-Content logs/security_events_*.json -Tail 20

# View all events
Get-Content logs/master_log_*.json -Tail 50
```

---

## 🎓 What You're Seeing

### Attack Flow Graph

The graph shows 3 main paths:

**Path 1: Attack Blocked** 🛑
```
MCP Server → Attack Payload → Security Layer → 🛑 BLOCKED
```

**Path 2: Action Allowed** ✓
```
MCP Server → Request → Security Layer → ✓ ALLOWED → Agent
```

**Path 3: Validation Stages**
```
Message → Protocol Check → Threat Detection → Policy Engine → Decision
```

### Color Coding

- 🔴 Red: Malicious/Dangerous
- 🟢 Green: Safe/Allowed
- 🟡 Yellow: Warning/Caution
- 🔵 Blue: Information/Process
- ⚫ Black: Neutral

---

## 💻 System Requirements

### Minimum
- Python 3.14+
- Node.js 16+
- 2GB RAM
- 500MB disk space

### Recommended
- Python 3.14+
- Node.js 18+
- 4GB RAM
- 2GB disk space

### Network
- Localhost network access (127.0.0.1)
- WebSocket support in browser
- Port 3000 (frontend)
- Port 8000 (backend)

---

## 🔐 Security Notes

The dashboard is designed for:
- **Development**: Testing on localhost
- **Testing**: Lab environment
- **Research**: Byzantine attack studies

For production use, see **DEPLOYMENT_GUIDE.md** for:
- HTTPS/WSS configuration
- Authentication setup
- Rate limiting
- Security headers

---

## 📞 Quick Reference

### Access Points
```
Frontend:     http://localhost:3000
Backend API:  http://localhost:8000/api
API Docs:     http://localhost:8000/docs
WebSocket:    ws://localhost:8000/ws/events
```

### Key Commands
```powershell
# Start backend
cd backend && .\start.bat

# Start frontend
cd frontend && .\start.bat

# Run test suite
python main.py

# View logs
ls logs/

# Stop services
# In each terminal, press Ctrl+C
```

### File Locations
```
Backend:      ./backend/
Frontend:     ./frontend/
Modules:      ./src/
Logs:         ./logs/
Reports:      ./reports/
Docs:         ./*.md
```

---

## ✨ Features at a Glance

✓ Real-time MCP connections
✓ 8 Byzantine attack scenarios
✓ Interactive attack flow visualization
✓ Live event streaming
✓ Security policy enforcement
✓ Comprehensive logging
✓ Web-based dashboard
✓ RESTful API with docs
✓ WebSocket real-time updates
✓ Production-ready code

---

## 🚀 You're All Set!

Everything is installed and configured. 

**Next:** Open http://localhost:3000 and start exploring!

For detailed information, see:
- **UI_GUIDE.md** - Full dashboard documentation
- **README.md** - Project overview
- **RESEARCH_REPORT.md** - Technical research details

---

**Version:** 1.0.0  
**Status:** ✅ Production Ready  
**Created:** March 29, 2026

**Questions?** Check the included documentation files or review the source code with detailed comments.
