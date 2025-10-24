from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QStatusBar, QMessageBox
from serial.tools import list_ports
from app.home.settings import Settings
from app.plot.plot_settings import PlotSettings

class Home(QMainWindow):

    def __init__(self, app):
        super().__init__()

        self.device = None

        self.setWindowTitle("Z-Scan Controller")

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")

        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        edit_menu = menu_bar.addMenu("&Edit")

        settings_action = edit_menu.addAction("Settings")

        self.devices_menu = menu_bar.addMenu("&Devices")
        self.devices_menu.aboutToShow.connect(self.reload_devices)

        help_menu = menu_bar.addMenu("&Help")

        about_action = help_menu.addAction("About")
        about_action.triggered.connect(lambda: QMessageBox.about(self, "About Z-Scan Controller", "Z-Scan Controller\n\nBy Carlos A. Vesga D.\n\nIn association with the GEOEL Group - Universidad del Atlántico\n\nhttps://github.com/SqrtMz/z-scan-software"))

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.statusBar().showMessage("Select a device")

        w = QWidget()
        self.setCentralWidget(w)

        layout = QHBoxLayout(w)

        self.settings = Settings(self)
        layout.addWidget(self.settings)
        self.settings.setMinimumWidth(275)
        self.settings.setMaximumWidth(300)

        self.plot_settings = PlotSettings(self)
        layout.addWidget(self.plot_settings)
        self.plot_settings.setMinimumSize(320, 240)

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