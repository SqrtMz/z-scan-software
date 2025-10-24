from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QComboBox, QSizePolicy, QGroupBox, QFormLayout, QSlider, QSpinBox, QDoubleSpinBox
from serial import Serial
from serial.serialutil import SerialException

class Settings(QWidget):
	def __init__(self, home_parent):
		super().__init__()

		self.home_parent = home_parent
		self.state = "Standby"

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

		move_from_label = QLabel("Move from:")
		move_from_label.setFixedSize(70, 15)
		self.move_from = QDoubleSpinBox()
		self.move_from.setDecimals(3)
		self.move_from.setRange(0, 100000)
		self.move_from.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		move_from_units = QLabel("cm")

		move_from_container = QHBoxLayout()
		move_from_container.addWidget(move_from_label)
		move_from_container.addWidget(self.move_from)
		move_from_container.addWidget(move_from_units)

		movement_group_layout.addRow(move_from_container)

		move_to_label = QLabel("Move to:")
		move_to_label.setFixedSize(70, 15)
		self.move_to = QDoubleSpinBox()
		self.move_to.setDecimals(3)
		self.move_to.setRange(0, 100000)
		self.move_to.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		move_to_units = QLabel("cm")

		move_to_container = QHBoxLayout()
		move_to_container.addWidget(move_to_label)
		move_to_container.addWidget(self.move_to)
		move_to_container.addWidget(move_to_units)

		movement_group_layout.addRow(move_to_container)

		self.cm_to_steps_label = QLabel("0 Steps", alignment=Qt.AlignmentFlag.AlignCenter)
		movement_group_layout.addWidget(self.cm_to_steps_label)

		self.move_from.valueChanged.connect(self.cm_to_steps)
		self.move_to.valueChanged.connect(self.cm_to_steps)

		self.motor_speed_label = QLabel("Motor speed: 1%")
		movement_group_layout.addRow(self.motor_speed_label)

		self.motor_speed = QSlider(Qt.Orientation.Horizontal)
		self.motor_speed.valueChanged.connect(self.update_slider_value)
		movement_group_layout.addRow(self.motor_speed)

		self.measure_separation = QSpinBox()
		self.measure_separation.setRange(0, 100000)
		self.measure_separation.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

		measure_separation_container = QHBoxLayout()
		measure_separation_label = QLabel("Measure separation:")
		measure_separation_label.setFixedSize(120, 15)

		measure_separation_container.addWidget(measure_separation_label)
		measure_separation_container.addWidget(self.measure_separation)
		measure_separation_container.addWidget(QLabel("cm"))
		movement_group_layout.addRow(measure_separation_container)

		self.stabilization_time = QSpinBox()
		self.stabilization_time.setRange(0, 100000)
		self.stabilization_time.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

		stabilization_time_container = QHBoxLayout()
		stabilization_time_label = QLabel("Stabilization time:")
		stabilization_time_label.setFixedSize(120, 15)
		stabilization_time_container.addWidget(stabilization_time_label)
		stabilization_time_container.addWidget(self.stabilization_time)
		stabilization_time_container.addWidget(QLabel("ms"))
		movement_group_layout.addRow(stabilization_time_container)

		distance_per_rev_label = QLabel("Distance per rev:")
		distance_per_rev_label.setFixedSize(120, 15)
		self.distance_per_rev = QDoubleSpinBox()
		self.distance_per_rev.setDecimals(3)
		self.distance_per_rev.setRange(0, 100000)
		self.distance_per_rev.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.distance_per_rev.valueChanged.connect(self.cm_to_steps)

		distance_per_rev_container = QHBoxLayout()
		distance_per_rev_container.addWidget(distance_per_rev_label)
		distance_per_rev_container.addWidget(self.distance_per_rev)
		distance_per_rev_container.addWidget(QLabel("cm"))
		movement_group_layout.addRow(distance_per_rev_container)

		microstep_label = QLabel("Microstep:")
		self.microstep = QComboBox()
		self.microstep.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.microstep.addItems(["1 - 200 pulses/rev", "2 - 400 pulses/rev", "4 - 800 pulses/rev", "8 - 1600 pulses/rev", "16 - 3200 pulses/rev", "32 - 6400 pulses/rev"])
		self.microstep.currentIndexChanged.connect(self.cm_to_steps)

		microstep_container = QHBoxLayout()
		microstep_container.addWidget(microstep_label)
		microstep_container.addWidget(self.microstep)
		movement_group_layout.addRow(microstep_container)

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


	def send_serial_command(self, command: str):
		if self.home_parent.device == None:
			self.home_parent.statusBar().showMessage("No device selected")
			return
		
		try:
			ser = Serial(self.home_parent.device, 115200)
			print(command)
			ser.write(command.encode("utf-8"))
			ser.close()
		
		except SerialException:
			self.home_parent.statusBar().showMessage("Invalid device, please check the device selected")
			return

	def start_execution(self):
		if self.home_parent.device == None:
			self.home_parent.statusBar().showMessage("No device selected")
			return
		
		try:
			move_from_pos = str(int(self.move_from.text())) + ','
			move_to_pos = str(int(self.move_to.text())) + ','
			motor_speed = str(self.motor_speed.value()) + ','
			measure_separation = str(int(self.measure_separation.text())) + ','
			stabilization_time = str(int(self.stabilization_time.text()))

		except ValueError:
			self.home_parent.statusBar().showMessage("Invalid position")
			return

		self.send_serial_command("execute," + move_from_pos + move_to_pos + motor_speed + measure_separation + stabilization_time)
		self.home_parent.plot_settings.reset_plot()
		self.start_data_collection()

	def start_data_collection(self):
		if self.home_parent.plot_settings.callback_id == None:

			def add_callback():
				self.home_parent.plot_settings.callback_id = self.home_parent.plot_settings.doc.add_periodic_callback(self.home_parent.plot_settings.update_function, 1)

			self.home_parent.plot_settings.doc.add_next_tick_callback(add_callback)

	def stop_data_collection(self):
		self.send_serial_command("stop,")

		if self.home_parent.plot_settings.callback_id != None:

			def remove_callback():
				try:
					self.home_parent.plot_settings.doc.remove_periodic_callback(self.home_parent.plot_settings.callback_id)
					self.home_parent.plot_settings.callback_id = None
				
				except ValueError:
					return

			self.home_parent.plot_settings.doc.add_next_tick_callback(remove_callback)

	def cm_to_steps(self):
		steps_per_rev = [200, 400, 800, 1600, 3200, 6400]
		distance_per_step = self.distance_per_rev.value() / steps_per_rev[self.microstep.currentIndex()]

		try:
			distance = self.move_to.value() - self.move_from.value()
			steps = int(round(distance / distance_per_step))

		except ZeroDivisionError:
			steps = 0

		self.cm_to_steps_label.setText(f"{steps} Steps")

	def update_slider_value(self):
		value = self.motor_speed.value()
		self.motor_speed_label.setText(f"Motor speed: {value + 1}%")

	def go_to_start(self):
		self.send_serial_command("go_to_start,")

	def go_to_end(self):
		self.send_serial_command("go_to_end,")

	def stop_and_restart(self):
		self.stop_data_collection()
		self.go_to_start()