import threading
import webbrowser
import time
import socket
from app import app

def wait_for_flask():
    """Wait until Flask is actually accepting connections, then open browser."""
    while True:
        try:
            sock = socket.create_connection(('localhost', 5001), timeout=1)
            sock.close()
            break
        except OSError:
            time.sleep(0.1)
    webbrowser.open('http://localhost:5001')

if __name__ == '__main__':
    # Wait for Flask to be ready, then open browser
    threading.Thread(target=wait_for_flask, daemon=True).start()
    # Start Flask
    app.run(debug=False, port=5001)