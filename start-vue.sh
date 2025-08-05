#!/bin/bash

# Network Ping Monitor - Vue.js Version
# This script starts both the backend and frontend

echo "🚀 Starting Network Ping Monitor (Vue.js Version)..."
echo "=================================================="

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill backend process and its children
    if [ ! -z "$BACKEND_PID" ]; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill -TERM $BACKEND_PID 2>/dev/null
        # Also kill any Python processes running main.py
        pkill -f "python.*main.py" 2>/dev/null
    fi
    
    # Kill frontend process and its children
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill -TERM $FRONTEND_PID 2>/dev/null
        # Also kill any npm serve processes
        pkill -f "npm.*serve" 2>/dev/null
    fi
    
    # Wait a moment for graceful shutdown
    sleep 2
    
    # Force kill if still running
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Force killing backend..."
        kill -KILL $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ] && kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Force killing frontend..."
        kill -KILL $FRONTEND_PID 2>/dev/null
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if Python backend is available
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the project root."
    exit 1
fi

# Check if Vue frontend is available
if [ ! -d "frontend-vue" ]; then
    echo "❌ Error: frontend-vue directory not found."
    exit 1
fi

# Start the Python backend
echo "🐍 Starting Python backend..."
# Try to use virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Using .venv virtual environment..."
    bash -c "source .venv/bin/activate; exec python main.py" &
    BACKEND_PID=$!
elif [ -d "venv" ]; then
    echo "Using venv virtual environment..."
    bash -c "source venv/bin/activate; exec python main.py" &
    BACKEND_PID=$!
elif command -v python3 &> /dev/null; then
    echo "Using system python3..."
    python3 main.py &
    BACKEND_PID=$!
elif command -v python &> /dev/null; then
    echo "Using system python..."
    python main.py &
    BACKEND_PID=$!
else
    echo "❌ Error: Python not found. Please install Python 3."
    exit 1
fi

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:5000/api/config > /dev/null 2>&1; then
    echo "❌ Backend failed to start. Please check if port 5000 is available."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend running on http://localhost:5000"

# Start the Vue.js frontend
echo "⚡ Starting Vue.js frontend..."
bash -c "cd frontend-vue && exec npm run serve" &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "❌ Frontend failed to start. Please check if port 3000 is available."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Frontend running on http://localhost:3000"
echo ""
echo "🎉 Network Ping Monitor is now running!"
echo "========================================"
echo "📊 Backend API:  http://localhost:5000"
echo "🌐 Frontend App: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes and handle termination
while kill -0 $BACKEND_PID 2>/dev/null && kill -0 $FRONTEND_PID 2>/dev/null; do
    sleep 1
done

# If we reach here, one of the processes died unexpectedly
echo "⚠️  One of the services stopped unexpectedly"
cleanup 