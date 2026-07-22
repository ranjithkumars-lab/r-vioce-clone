#!/bin/bash

# Voice Studio - Single Terminal Start Script (Non-Docker)

echo "Starting Voice Studio..."

# Cleanup function to kill all background processes on exit
cleanup() {
    echo ""
    echo "Stopping all services..."
    kill $(jobs -p) 2>/dev/null
    wait $(jobs -p) 2>/dev/null
    echo "Voice Studio stopped."
    exit
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT SIGTERM

# 1. Setup and start Backend API & Worker
echo "[Backend] Setting up virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

echo "[Backend API] Starting Uvicorn..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 > ../api.log 2>&1 &
API_PID=$!

echo "[Backend Worker] Starting Daemon..."
python worker_main.py > ../worker.log 2>&1 &
WORKER_PID=$!
cd ..

# 2. Setup and start Frontend
echo "[Frontend] Installing dependencies and starting React server..."
cd frontend
npm install --silent
npm run dev -- --host 0.0.0.0 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "====================================================="
echo "✅ Voice Studio is running in the background!"
echo "   - Frontend UI: http://localhost:5173"
echo "   - Backend API: http://localhost:8000/docs"
echo ""
echo "📜 Logs are being written to:"
echo "   - api.log"
echo "   - worker.log"
echo "   - frontend.log"
echo ""
echo "Press Ctrl+C to stop all services."
echo "====================================================="

# Wait indefinitely until interrupted
wait
