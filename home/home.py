from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
import serial.tools.list_ports
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class Home(QMainWindow):
    
    def __init__(self, app):
        super().__init__()
        self.app = app

        self.setWindowTitle("Home")

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        self.devices_menu = menu_bar.addMenu("&Devices")
        self.devices_menu.aboutToShow.connect(self.reload_devices)

        w = QWidget()
        self.setCentralWidget(w)

        self.text = QPushButton("Text")

        x = []
        y = []

        fig = Figure()
        ax = fig.add_subplot()
        ax.plot(x, y)
        canvas = FigureCanvasQTAgg(fig)

        layout = QHBoxLayout()
        layout.addWidget(self.text)
        layout.addWidget(canvas)

        w.setLayout(layout)
    
    def reload_devices(self):
        devices = [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]

        self.devices_menu.clear()

        if not devices:
             self.devices_menu.addAction("No devices connected").setEnabled(False)
        
        for dev in devices:
            self.devices_menu.addAction(dev)