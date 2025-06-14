from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit
from PySide6.QtWebEngineWidgets import QWebEngineView
from serial.tools import list_ports
from serial import Serial

class Home(QMainWindow):
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.device = None

        self.doc = None
        self.update_function = None
        self.callback_id = None

        self.setWindowTitle("Home")

        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        quit_action = file_menu.addAction("Quit")
        quit_action.triggered.connect(self.close)

        self.devices_menu = menu_bar.addMenu("&Devices")
        self.devices_menu.aboutToShow.connect(self.reload_devices)

        w = QWidget()
        self.setCentralWidget(w)

        layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        layout.addLayout(input_layout)

        self.selected_device_label = QLabel("Select a device")
        input_layout.addWidget(self.selected_device_label)

        motor_steps_layout = QHBoxLayout()
        motor_steps_label = QLabel("Motor steps:")
        self.motor_steps = QLineEdit()

        input_layout.addLayout(motor_steps_layout)
        motor_steps_layout.addWidget(motor_steps_label)
        motor_steps_layout.addWidget(self.motor_steps)

        # Testing ############################################
        command_test_layout = QHBoxLayout()
        command_test_label = QLabel("Command test:")
        self.command_test = QLineEdit()

        input_layout.addLayout(command_test_layout)
        command_test_layout.addWidget(command_test_label)
        command_test_layout.addWidget(self.command_test)
        ######################################################

        self.plot = QWebEngineView()
        self.plot.setUrl("http://localhost:5006/")
        layout.addWidget(self.plot)

        actions_layout = QHBoxLayout()
        input_layout.addLayout(actions_layout)

        self.execute = QPushButton("Execute")
        self.execute.clicked.connect(self.start_execution)

        self.go_to_start_button = QPushButton("Go to start")
        self.go_to_start_button.clicked.connect(self.go_to_start)

        self.go_to_end_button = QPushButton("Go to end")
        self.go_to_end_button.clicked.connect(self.go_to_end)

        actions_layout.addWidget(self.execute)
        actions_layout.addWidget(self.go_to_start_button)
        actions_layout.addWidget(self.go_to_end_button)

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
        self.selected_device_label.setText(f"Selected device: {device}")
    
    def start_execution(self):

        if self.device == None:
            print("No device selected")
            return

        try:
            steps = int(self.motor_steps.text())
            command_test = self.command_test.text()

        except ValueError:
            print("Invalid number of steps")
            return
        
        ser = Serial(self.device, 115200)
        ser.write(f"{command_test}".encode("utf-8"))
        ser.close()

        self.go_to_start()
        self.start_data_collection()

    def go_to_start(self):
        ser = Serial(self.device, 115200)
        ser.write("go_to_start".encode("utf-8"))
        ser.close()

    def go_to_end(self):
        ser = Serial(self.device, 115200)
        ser.write("go_to_end".encode("utf-8"))
        ser.close()

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