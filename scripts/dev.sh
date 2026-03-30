#!/bin/bash
# Development launcher: starts Python sidecar + Tauri dev

echo "=== MoneyPrinterTurbo Desktop (dev mode) ==="

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Start Python sidecar in background
echo "Starting Python sidecar on port 18080..."
python main.py --port 18080 --mode desktop &
SIDECAR_PID=$!
echo "Sidecar PID: $SIDECAR_PID"

# Wait for sidecar to be ready
echo "Waiting for sidecar..."
for i in $(seq 1 30); do
    if curl -s http://127.0.0.1:18080/api/v1/ping > /dev/null 2>&1; then
        echo "Sidecar ready!"
        break
    fi
    sleep 1
done

# Start Tauri dev (if desktop/ exists)
if [ -d "desktop" ]; then
    echo "Starting Tauri dev..."
    cd desktop
    npm run tauri dev
else
    echo "desktop/ directory not found. Running sidecar only."
    echo "Press Ctrl+C to stop."
    wait $SIDECAR_PID
fi

# Cleanup
kill $SIDECAR_PID 2>/dev/null
echo "Dev environment stopped."
