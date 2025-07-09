from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStatusBar
from serial.tools import list_ports
import pandas as pd
from home.settings import Settings
from home.plot import PlotSettings

class Home(QMainWindow):

    def __init__(self):
        super().__init__()
        self.device = None

        self.df = pd.DataFrame(columns=['x', 'y'])

        self.doc = None
        self.update_function = None
        self.callback_id = None

        self.setWindowTitle("Home")

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")

        quit_action = file_menu.addAction("Quit")
        quit_action.setStatusTip("Close this program")
        quit_action.triggered.connect(self.close)

        self.devices_menu = menu_bar.addMenu("&Devices")
        self.devices_menu.aboutToShow.connect(self.reload_devices)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.statusBar().showMessage("Select a device")

        w = QWidget()
        self.setCentralWidget(w)

        layout = QHBoxLayout()

        self.settings = Settings(self)
        layout.addLayout(self.settings.input_layout)

        self.plot_settings = PlotSettings()
        layout.addWidget(self.plot_settings.plot_group)

        w.setLayout(layout)


    def reload_devices(self):

        available_devices = [tuple(p)[0] for p in list(list_ports.comports())]
        dev_actions = []

        self.devices_menu.clear()

        if not available_devices:
             self.devices_menu.addAction("No devices connected").setEnabled(False)
        
        for dev in available_devices:
            dev_actions.append(self.devices_menu.addAction(dev))

        for action in dev_actions:
            action.triggered.connect(lambda s, dev=action: self.select_device(dev.text()))

    def select_device(self, device):
        self.device = device
        self.settings.selected_device.setText(f"Selected device: {device}")