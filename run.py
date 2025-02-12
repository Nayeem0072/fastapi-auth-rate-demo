import uvicorn
import subprocess
import sys
import signal
import threading

def stream_logs(process, prefix):
    """Stream logs from a process with a prefix"""
    for line in iter(process.stdout.readline, ''):
        print(f"{prefix}: {line.strip()}")
    for line in iter(process.stderr.readline, ''):
        print(f"{prefix} ERROR: {line.strip()}")

def run_services():
    """Run both services using subprocess"""
    print("Starting services...")
    
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend_service:backend", "--host", "0.0.0.0", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    
    gateway = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "gateway:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=1,
        universal_newlines=True
    )
    
    # Start log streaming threads
    backend_log_thread = threading.Thread(target=stream_logs, args=(backend, "Backend"))
    gateway_log_thread = threading.Thread(target=stream_logs, args=(gateway, "Gateway"))
    
    backend_log_thread.daemon = True
    gateway_log_thread.daemon = True
    
    backend_log_thread.start()
    gateway_log_thread.start()
    
    def signal_handler(sig, frame):
        print("\nShutting down services...")
        backend.terminate()
        gateway.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        backend.wait()
        gateway.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    run_services()
