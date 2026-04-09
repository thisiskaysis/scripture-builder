import threading
import webbrowser
import socket
import rumps
from app import app as flask_app


def wait_for_flask():
    """Wait until Flask is actually accepting connections, then open browser."""
    while True:
        try:
            sock = socket.create_connection(('localhost', 5001), timeout=1)
            sock.close()
            break
        except OSError:
            import time
            time.sleep(0.1)
    webbrowser.open('http://localhost:5001')


def start_flask():
    """Run Flask in a background thread."""
    flask_app.run(debug=False, port=5001)


class ScriptureBuilderApp(rumps.App):
    def __init__(self):
        super(ScriptureBuilderApp, self).__init__(
            name='Scripture Builder',
            title='📖',
            quit_button=None
        )
        self.menu = [
            rumps.MenuItem('Open in Browser', callback=self.open_browser),
            rumps.separator,
            rumps.MenuItem('Quit Scripture Builder', callback=self.quit_app),
        ]

    def open_browser(self, _):
        webbrowser.open('http://localhost:5001')

    def quit_app(self, _):
        rumps.quit_application()


if __name__ == '__main__':
    # Start Flask in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Wait for Flask then open browser
    browser_thread = threading.Thread(target=wait_for_flask, daemon=True)
    browser_thread.start()

    # Start menu bar app — this blocks until quit
    ScriptureBuilderApp().run()