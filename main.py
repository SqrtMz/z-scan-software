import sys
from threading import Thread
from PySide6.QtWidgets import QApplication
from app.windows.home import Home
from app.plot.plot import create_new_plot
from bokeh.server.server import Server
from tornado.ioloop import IOLoop

app = QApplication(sys.argv)

window = Home(app)
window.resize(1280, 720)
window.show()

def start_bokeh():
	server = Server({'/': lambda doc: create_new_plot(doc, window)}, io_loop=IOLoop.current(), allow_websocket_origin=["localhost:5006"], port=5006)
	server.start()
	server.io_loop.start()

if __name__ == "__main__":

	t = Thread(target=start_bokeh, daemon=True).start()

	sys.exit(app.exec())