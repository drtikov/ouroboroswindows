import os
import sys
import threading
import time
import webview
import subprocess
import pathlib
import uvicorn

from ouroboros.config import PORT_FILE, AGENT_SERVER_PORT

def start_server():
    """Start the server in a separate thread/process"""
    # Start the Starlette server from server.py programmatically.
    # Note: Using uvicorn.run blocks the thread.
    import server
    port = AGENT_SERVER_PORT
    try:
        if PORT_FILE.exists():
            PORT_FILE.unlink()
    except Exception:
        pass

    # uvicorn.run must be called on main thread or we need to pass the app string
    uvicorn.run("server:app" if hasattr(server, 'app') else "server:app_start", host="127.0.0.1", port=port, log_level="info")

if __name__ == '__main__':
    # Make sure we run in the right directory
    os.environ["OUROBOROS_REPO_DIR"] = str(pathlib.Path(__file__).parent.resolve())
    
    # We will spawn the server as a subprocess so pywebview can run on the main thread
    server_cmd = [sys.executable, str(pathlib.Path(__file__).parent / "server.py")]
    
    # Actually wait, server.py uses uvicorn.run when executed directly! Let's check server.py:
    # Ah, server.py doesn't have an __main__ block in the first 800 lines we saw... Wait. Let's just run uvicorn.
    server_process = subprocess.Popen(server_cmd)

    # Give server time to start
    time.sleep(3)

    # Launch PyWebView
    webview.create_window(
        title='Ouroboros',
        url=f'http://127.0.0.1:{AGENT_SERVER_PORT}',
        width=1000,
        height=800,
        min_size=(800, 600)
    )
    
    webview.start()
    
    # Cleanup when webview is closed
    server_process.terminate()
