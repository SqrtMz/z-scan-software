import sys
from threading import Thread
from PySide6.QtWidgets import QApplication
from home.home import Home
from bokeh.server.server import Server
from tornado.ioloop import IOLoop
from home.bokeh import update_plot

app = QApplication(sys.argv)

w = Home(app)
w.resize(1280, 720)
w.show()

def start_bokeh():
    server = Server({'/': lambda doc: update_plot(doc, w)}, io_loop=IOLoop.current(), allow_websocket_origin=["localhost:5006"])
    server.start()
    server.io_loop.start()

if __name__ == "__main__":

    t = Thread(target=start_bokeh, daemon=True).start()
    sys.exit(app.exec())