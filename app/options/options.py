from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QSizePolicy, QGroupBox, QFormLayout, QSlider, QSpinBox, QDoubleSpinBox
from serial import Serial
from serial.serialutil import SerialException
from app.util.form_cell_units import FormCellUnits

class Options(QWidget):
	def __init__(self, home_parent):
		super().__init__()

		self.home_parent = home_parent
		self.plot = None
		self.state = "Standby"
		self.distance_per_step = 0

		self.main_layout = QVBoxLayout(self)

		#####################
		# Information group #
		#####################
		information_layout = QFormLayout()
		information_group = QGroupBox("Information")
		information_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
		information_group.setLayout(information_layout)

		self.selected_device = QLabel("Select a device")
		information_layout.addRow(self.selected_device)

		self.motor_state = QLabel(f"Current state: {self.state}")
		information_layout.addRow(self.motor_state)

		self.main_layout.addWidget(information_group)

		##################
		# Movement group #
		##################
		movement_group_layout = QFormLayout()
		movement_group = QGroupBox("Movement options")
		movement_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		movement_group.setLayout(movement_group_layout)

		self.move_from = FormCellUnits("Move from:", QDoubleSpinBox(), "cm", label_x_size=70, label_y_size=15, update_value_function=self.update_movement_options)
		movement_group_layout.addRow(self.move_from)

		self.move_to = FormCellUnits("Move to:", QDoubleSpinBox(), "cm", label_x_size=70, label_y_size=15, update_value_function=self.update_movement_options)
		movement_group_layout.addRow(self.move_to)

		self.update_movement_options_label = QLabel("0 Steps", alignment=Qt.AlignmentFlag.AlignCenter)
		movement_group_layout.addWidget(self.update_movement_options_label)

		self.motor_speed_label = QLabel("Motor speed: 1%")
		movement_group_layout.addRow(self.motor_speed_label)

		self.motor_speed = QSlider(Qt.Orientation.Horizontal)
		self.motor_speed.valueChanged.connect(self.update_slider_value)
		movement_group_layout.addRow(self.motor_speed)

		self.measure_separation = FormCellUnits("Measure separation:", QDoubleSpinBox(), "cm")
		movement_group_layout.addRow(self.measure_separation)

		self.stabilization_time = FormCellUnits("Stabilization time:", QSpinBox(), "ms")
		movement_group_layout.addRow(self.stabilization_time)

		self.distance_per_rev = FormCellUnits("Distance per rev:", QDoubleSpinBox(), "cm", update_value_function=self.update_movement_options)
		movement_group_layout.addRow(self.distance_per_rev)

		self.microstep = QComboBox()
		self.microstep.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.microstep.addItems(["1 - 200 pulses/rev", "2 - 400 pulses/rev", "4 - 800 pulses/rev", "8 - 1600 pulses/rev", "16 - 3200 pulses/rev", "32 - 6400 pulses/rev"])
		self.microstep.currentIndexChanged.connect(self.update_movement_options)
		movement_group_layout.addRow(QLabel("Microstep:"), self.microstep)

		self.main_layout.addWidget(movement_group)

		#################
		# Actions group #
		#################
		actions_group = QGroupBox("Actions")
		actions_layout = QVBoxLayout()
		actions_group.setLayout(actions_layout)
		actions_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

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

		actions_row2 = QHBoxLayout()

		self.stop = QPushButton("Stop")
		self.stop.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.stop.clicked.connect(self.stop_data_collection)
		actions_row2.addWidget(self.stop)

		self.restart = QPushButton("Restart")
		self.restart.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
		self.restart.clicked.connect(self.stop_and_restart)
		actions_row2.addWidget(self.restart)

		actions_layout.addLayout(actions_row2)

		self.main_layout.addWidget(actions_group)

	def send_serial_command(self, command: str, device: str):
		if device == None:
			self.home_parent.statusBar().showMessage("No device selected")
			return
		
		try:
			ser = Serial(device, 115200)
			print(command)
			ser.write(command.encode("utf-8"))
			ser.close()
		
		except SerialException:
			self.home_parent.statusBar().showMessage("Invalid device, please check the device selected")
			return

	def start_execution(self):
		try:
			move_from_pos = str(int(self.move_from.value() / self.distance_per_step)) + ','
			move_to_pos = str(int(self.move_to.value() / self.distance_per_step)) + ','
			motor_speed = str(self.motor_speed.value() + 1) + ','
			measure_separation = str(int(self.measure_separation.value() / self.distance_per_step)) + ','
			stabilization_time = str(int(self.stabilization_time.value()))

		except ValueError:
			self.home_parent.statusBar().showMessage("Invalid position")
			return

		self.send_serial_command("execute," + move_from_pos + move_to_pos + motor_speed + measure_separation + stabilization_time, self.home_parent.device)
		self.start_data_collection()

	def start_data_collection(self):
		if self.home_parent.plot_options.callback_id == None:

			def add_callback():
				self.home_parent.plot_options.callback_id = self.home_parent.plot_options.doc.add_periodic_callback(self.home_parent.plot_options.update_function, 1)

			self.home_parent.plot_options.doc.add_next_tick_callback(add_callback)

	def stop_data_collection(self):
		self.send_serial_command("stop,", self.home_parent.device)

		if self.home_parent.plot_options.callback_id != None:

			def remove_callback():
				try:
					self.home_parent.plot_options.doc.remove_periodic_callback(self.home_parent.plot_options.callback_id)
					self.home_parent.plot_options.callback_id = None
				
				except ValueError:
					return

			self.home_parent.plot_options.doc.add_next_tick_callback(remove_callback)

	def update_movement_options(self):
		steps_per_rev = [200, 400, 800, 1600, 3200, 6400]

		distance_per_step = self.distance_per_rev.value() / steps_per_rev[self.microstep.currentIndex()]
		self.distance_per_step = distance_per_step

		try:
			distance = self.move_to.value() - self.move_from.value()
			steps = int(round(distance / distance_per_step))

		except ZeroDivisionError:
			steps = 0

		self.update_movement_options_label.setText(f"{steps} Steps")

		self.move_from.input_widget.setRange(0, self.move_to.value())
		self.move_to.input_widget.setRange(self.move_from.value(), 100000)
		
		def update():
			self.plot.x_range.start = int(round(self.move_from.value() - 2))
			self.plot.x_range.end = int(round(self.move_to.value() + 2))

		self.home_parent.plot_options.doc.add_next_tick_callback(update)

	def update_slider_value(self):
		value = self.motor_speed.value()
		self.motor_speed_label.setText(f"Motor speed: {value + 1}%")

	def go_to_start(self):
		self.send_serial_command("go_to_start,", self.home_parent.device)

	def go_to_end(self):
		self.send_serial_command("go_to_end,", self.home_parent.device)

	def stop_and_restart(self):
		self.stop_data_collection()
		self.go_to_start()