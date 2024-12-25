import sys
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QComboBox
import serial.tools.list_ports

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
        # reload_devices_action = self.devices_menu.addAction("Reload connected devices list")
        # reload_devices_action.triggered.connect(self.reload_devices)

        w = QWidget()
        self.setCentralWidget(w)

        device_selection = QComboBox()
        self.devices = [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]
        device_selection.addItems(self.devices)


        main_layout = QVBoxLayout()
        main_layout.addWidget(device_selection)

        w.setLayout(main_layout)

    
    def reload_devices(self):
        devices = [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]

        self.devices_menu.clear()

        if not devices:
             self.devices_menu.addAction("No devices connected").setEnabled(False)
        
        for dev in devices:
                self.devices_menu.addAction(dev)