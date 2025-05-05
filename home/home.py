from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit
from serial.tools import list_ports
from serial import Serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

class Home(QMainWindow):
    
    def __init__(self, app):
        super().__init__()

        self.app = app
        self.device = None

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

        actions_layout = QHBoxLayout()
        input_layout.addLayout(actions_layout)

        self.execute = QPushButton("Execute")
        self.execute.clicked.connect(self.send_info_to_mcu)

        self.go_to_start = QPushButton("Go to start")
        self.go_to_start.clicked.connect(lambda: print("Go to start button clicked"))

        self.go_to_end = QPushButton("Go to end")
        self.go_to_end.clicked.connect(lambda: print("Go to end button clicked"))

        actions_layout.addWidget(self.execute)
        actions_layout.addWidget(self.go_to_start)
        actions_layout.addWidget(self.go_to_end)

        self.mcu_time = [0, 1, 2, 3, 4, 5]
        self.mcu_voltage = [0, 1, 4, 9, 16, 25]

        fig = Figure()
        ax = fig.add_subplot()
        ax.plot(self.mcu_time, self.mcu_voltage)
        canvas = FigureCanvasQTAgg(fig)

        layout.addWidget(canvas)

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

    
    def send_info_to_mcu(self):

        if self.device is None:
            print("No device selected")
            return

        try:
            steps = int(self.motor_steps.text())
        except ValueError:
            print("Invalid number of steps")
            return
        
        ser = Serial(self.device, 115200)
        ser.write(f"steps: {steps}".encode("utf-8"))
        ser.close()