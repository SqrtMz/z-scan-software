import sys
from time import sleep
from threading import Thread
import socket
from PySide6.QtWidgets import QApplication
from app.gui.home import Home
from app.plot.plot import create_new_plot
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

app = QApplication(sys.argv)

portx = 1024

while(True):
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		try:
			s.bind(("localhost", portx))
			break
		except OSError:
			portx += 1

print(f"Port {portx} will be used...")

window = Home(app, portx)
window.resize(1280, 720)
window.show()

def start_bokeh():
	server = Server({'/': lambda doc: create_new_plot(doc, window)}, io_loop=IOLoop.current(), allow_websocket_origin=[f"localhost:{portx}"], port=portx)
	server.start()
	server.io_loop.start()

if __name__ == "__main__":

	t = Thread(target=start_bokeh, daemon=True).start()

	sys.exit(app.exec())