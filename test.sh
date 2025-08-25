#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🧪 Testing Purretys Setup${NC}"
echo "=========================="
echo ""

# Function to test command
test_command() {
    local description="$1"
    local command="$2"
    
    echo -n "Testing $description... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# Test Node and npm
echo -e "${BLUE}1. Testing Node.js Environment${NC}"
echo "------------------------------"
test_command "Node.js installation" "node --version"
test_command "npm installation" "npm --version"
test_command "Root package.json" "node -e \"require('./package.json')\""

echo ""
echo -e "${BLUE}2. Testing Python Environment${NC}"
echo "-----------------------------"
test_command "Python installation" "python --version || python3 --version"
test_command "pip installation" "pip --version || pip3 --version"

# Test backend
echo ""
echo -e "${BLUE}3. Testing Backend Setup${NC}"
echo "------------------------"

if [ -f "backend/app/main.py" ]; then
    echo -n "Testing FastAPI import... "
    cd backend
    if python -c "from app.main import app" 2>/dev/null || python3 -c "from app.main import app" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC} - Try activating venv first"
    fi
    cd ..
else
    echo -e "${YELLOW}Skipping backend tests - main.py not found${NC}"
fi

# Test frontend
echo ""
echo -e "${BLUE}4. Testing Frontend Setup${NC}"
echo "-------------------------"

if [ -f "frontend/package.json" ]; then
    cd frontend
    test_command "Frontend package.json" "node -e \"require('./package.json')\""
    
    if [ -d "node_modules" ]; then
        test_command "React dependency" "node -e \"require('react/package.json')\""
        test_command "Vite dependency" "node -e \"require('vite/package.json')\""
    else
        echo -e "${YELLOW}Frontend node_modules not installed${NC}"
    fi
    cd ..
fi

# Test TypeScript
echo ""
echo -e "${BLUE}5. Testing TypeScript Setup${NC}"
echo "---------------------------"
test_command "TypeScript in frontend" "cd frontend && npx tsc --version"

# Try to start servers (with timeout)
echo ""
echo -e "${BLUE}6. Server Start Test${NC}"
echo "--------------------"

echo -e "${YELLOW}Attempting to start backend server (5-second test)...${NC}"
timeout 5 bash -c "cd backend && python -m uvicorn app.main:app --port 8001" > /dev/null 2>&1 &
BACKEND_PID=$!
sleep 2

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend server can start"
else
    echo -e "${YELLOW}!${NC} Backend server couldn't be tested (may need venv activation)"
fi
kill $BACKEND_PID 2>/dev/null

echo ""
echo "=========================="
echo -e "${BLUE}Quick Health Check Results${NC}"
echo "=========================="

# Final summary
ALL_GOOD=true

# Check critical files
echo ""
echo "Critical Files:"
[ -f "package.json" ] && echo -e "${GREEN}✓${NC} Root package.json" || { echo -e "${RED}✗${NC} Root package.json"; ALL_GOOD=false; }
[ -f "frontend/package.json" ] && echo -e "${GREEN}✓${NC} Frontend package.json" || { echo -e "${RED}✗${NC} Frontend package.json"; ALL_GOOD=false; }
[ -f "backend/requirements.txt" ] && echo -e "${GREEN}✓${NC} Backend requirements" || { echo -e "${RED}✗${NC} Backend requirements"; ALL_GOOD=false; }

echo ""
echo "Dependencies:"
[ -d "node_modules" ] && echo -e "${GREEN}✓${NC} Root dependencies" || echo -e "${YELLOW}!${NC} Run: npm install"
[ -d "frontend/node_modules" ] && echo -e "${GREEN}✓${NC} Frontend dependencies" || echo -e "${YELLOW}!${NC} Run: cd frontend && npm install"
[ -d "backend/venv" ] || [ -d "backend/.venv" ] && echo -e "${GREEN}✓${NC} Python virtualenv" || echo -e "${YELLOW}!${NC} Run: cd backend && python -m venv venv"

echo ""
if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ Setup looks good!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "2. Start frontend: cd frontend && npm run dev"
    echo "3. Visit: http://localhost:5173"
else
    echo -e "${YELLOW}⚠ Some setup steps are incomplete${NC}"
    echo ""
    echo "Run these commands to complete setup:"
    echo "1. npm install"
    echo "2. cd frontend && npm install"
    echo "3. cd ../backend && python -m venv venv"
    echo "4. source backend/venv/bin/activate"
    echo "5. pip install -r backend/requirements.txt"
fi