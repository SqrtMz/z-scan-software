from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QSizePolicy, QStatusBar, QGroupBox, QFormLayout, QComboBox, QFileDialog
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from serial.tools import list_ports
from serial import Serial
from serial.serialutil import SerialException
import pandas as pd

class Home(QMainWindow):
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.device = None
        self.state = "Standby"

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

        w = QWidget()
        self.setCentralWidget(w)

        layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        layout.addLayout(input_layout)

        information_group = QGroupBox("Information")
        information_layout = QHBoxLayout()
        information_group.setLayout(information_layout)
        
        self.selected_device = QLabel("Select a device")
        information_layout.addWidget(self.selected_device)

        self.information_test1 = QLabel(f"Current state: {self.state}")
        information_layout.addWidget(self.information_test1)

        input_layout.addWidget(information_group)

        distance_group = QGroupBox("Distance options")
        distance_group_layout = QFormLayout()
        distance_group.setLayout(distance_group_layout)
        
        self.move_to = QLineEdit()
        distance_group_layout.addRow(QLabel("Move to:"), self.move_to)

        self.current_position = QLabel()
        self.current_position.setText("NA")
        distance_group_layout.addRow(QLabel("Current position:"), self.current_position)

        input_layout.addWidget(distance_group)

        movement_group = QGroupBox("Movement options")
        movement_layout = QFormLayout()
        movement_group.setLayout(movement_layout)

        self.step_size_selector = QComboBox()
        self.step_size_selector.addItems(["Full step", "1/2 step", "1/4 step", "1/8 step"])
        movement_layout.addRow(QLabel("Motor step size:"), self.step_size_selector)
        self.step_size_selector.currentTextChanged.connect(self.step_size_changed)

        input_layout.addWidget(movement_group)

        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        actions_group.setLayout(actions_layout)

        actions_row1 = QHBoxLayout()

        self.execute = QPushButton("Execute")
        self.execute.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.execute.clicked.connect(self.start_execution)
        actions_row1.addWidget(self.execute)

        self.go_to_start_button = QPushButton("Go to start")
        self.go_to_start_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.go_to_start_button.clicked.connect(self.go_to_start)
        actions_row1.addWidget(self.go_to_start_button)

        self.go_to_end_button = QPushButton("Go to end")
        self.go_to_end_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.go_to_end_button.clicked.connect(self.go_to_end)
        actions_row1.addWidget(self.go_to_end_button)

        actions_layout.addLayout(actions_row1)

        input_layout.addWidget(actions_group)

        plot_group = QGroupBox("Plot")
        plot_layout = QVBoxLayout()
        plot_group.setLayout(plot_layout)

        self.plot = QWebEngineView()
        self.plot.setUrl("http://localhost:5006/")
        self.plot.setFixedSize(1280, 720)
        self.plot.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        plot_layout.addWidget(self.plot, alignment=Qt.AlignmentFlag.AlignCenter)
        profile = QWebEngineProfile.defaultProfile()
        profile.downloadRequested.connect(self.capture_plot)

        plot_actions_layout = QVBoxLayout()

        plot_actions_row1 = QHBoxLayout()

        self.save_plot_data_button = QPushButton("Save plot data")
        self.save_plot_data_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.save_plot_data_button.clicked.connect(self.save_plot_data)
        plot_actions_row1.addWidget(self.save_plot_data_button)

        self.reset_plot_button = QPushButton("Reset plot")
        self.reset_plot_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.reset_plot_button.clicked.connect(self.reset_plot)
        plot_actions_row1.addWidget(self.reset_plot_button)

        plot_actions_layout.addLayout(plot_actions_row1)
        plot_layout.addLayout(plot_actions_layout)

        layout.addWidget(plot_group)

        w.setLayout(layout)

        self.setStatusBar(QStatusBar(self))
        self.statusBar().showMessage("Select a device")

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
        self.selected_device.setText(f"Selected device: {device}")
    
    def send_serial_command(self, command: str):

        if self.device == None:
            self.statusBar().showMessage("No device selected")
            return
        
        try:
            ser = Serial(self.device, 115200)
            ser.write(command.encode("utf-8"))
            ser.close()
        
        except SerialException:
            self.statusBar().showMessage("Invalid device, please check the device selected")
            return

    def start_execution(self):
        try:
            new_position = int(self.move_to.text())

        except ValueError:
            self.statusBar().showMessage("Invalid position")
            return

        self.send_serial_command(new_position)

        self.go_to_start()
        self.start_data_collection()

    def go_to_start(self):
        self.send_serial_command("go_to_start")

    def go_to_end(self):
        self.send_serial_command("go_to_end")

    def go_to_distance(self):
        return

    def start_data_collection(self):
        if self.callback_id == None:

            def add_callback():
                self.callback_id = self.doc.add_periodic_callback(self.update_function, 1)

            self.doc.add_next_tick_callback(add_callback)
                

    def stop_data_collection(self):
        if self.callback_id != None:

            def remove_callback():
                self.doc.remove_periodic_callback(self.callback_id)
                self.callback_id = None

            self.doc.add_next_tick_callback(remove_callback)

    def step_size_changed(self, text):
        print(text)

    def capture_plot(self, download):
        default_filename = download.suggestedFileName()

        path, _ = QFileDialog.getSaveFileName(self, "Save File As", default_filename + ".png", "PNG Image (*.png);; All Files (*)")
        
        if path:
            download.setDownloadFileName(path)
            download.accept()

    def save_plot_data(self):

        path, _ = QFileDialog.getSaveFileName(self, "Save File As", "data.csv", "CSV Files (*.csv);;All Files (*)")

        if path:
            self.df.to_csv(path, index=False)
    
    def reset_plot(self):
        self.df = pd.DataFrame(columns=['x', 'y'])