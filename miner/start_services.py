import os
import sys
import subprocess
import time
import signal
import argparse

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    parser = argparse.ArgumentParser(description="Start the AMAIAS MINER services")
    parser.add_argument("--api-only", action="store_true", help="Start only the API server")
    parser.add_argument("--worker-only", action="store_true", help="Start only the background worker")
    return parser.parse_args()


def start_api():
    """Start the Flask API server"""
    print("Starting API server...")
    api_process = subprocess.Popen(
        [sys.executable, os.path.join(THIS_DIR, "app.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    return api_process


def start_worker():
    """Start the background worker process"""
    print("Starting background worker...")
    worker_process = subprocess.Popen(
        [sys.executable, os.path.join(THIS_DIR, "worker.py")],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    return worker_process


def monitor_output(process, prefix):
    """Monitor and print output from a process"""
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            print(f"{prefix}: {line.rstrip()}")


def main():
    args = parse_args()
    processes = []
    
    try:
        # Start the API server if requested or if no specific service is selected
        if not args.worker_only:
            api_process = start_api()
            processes.append(("API", api_process))
        
        # Start the worker if requested or if no specific service is selected
        if not args.api_only:
            worker_process = start_worker()
            processes.append(("Worker", worker_process))
        
        # Monitor process output in the main thread
        while True:
            for prefix, process in processes:
                line = process.stdout.readline() if process.stdout else None
                if line:
                    print(f"{prefix}: {line.rstrip()}")
                elif process.poll() is not None:
                    print(f"{prefix} process terminated with code {process.returncode}")
                    raise KeyboardInterrupt  # Trigger shutdown of all processes
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("Shutting down...")
        # Terminate all processes on Ctrl+C
        for _, process in processes:
            try:
                process.send_signal(signal.SIGINT)
                time.sleep(1)
                if process.poll() is None:
                    process.terminate()
            except:
                pass
        
if __name__ == "__main__":
    main()
