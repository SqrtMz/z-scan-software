from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QDoubleSpinBox, QGroupBox, QSizePolicy, QPushButton, QLabel, QVBoxLayout, QSpacerItem, QHBoxLayout, QFileDialog, QRadioButton, QButtonGroup
from app.gui.form_cell_units import FormCellUnits
import pandas as pd

from app.plot.plot import create_new_plot

class Calculation(QGroupBox):
	def __init__(self, home_parent):
		super().__init__()

		self.home_parent = home_parent
		self.n2 = 0

		self.setTitle("Calculations")
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

		layout = QVBoxLayout(self)
		self.setLayout(layout)

		form_layout = QFormLayout()

		file_picker_layout = QHBoxLayout()

		file_picker_label = QLabel("Select a data file:")
		file_picker_label.setFixedSize(175, 15)
		file_picker_layout.addWidget(file_picker_label)

		self.file_picker_button = QPushButton("No file selected...")
		self.file_picker_button.clicked.connect(self.load_file)

		file_picker_layout.addWidget(self.file_picker_button)

		form_layout.addRow(file_picker_layout)

		self.laser_wavelength = FormCellUnits("Laser wavelength:", QDoubleSpinBox(), "nm", input_widget_value=0)
		form_layout.addRow(self.laser_wavelength)

		self.laser_power = FormCellUnits("Laser power:", QDoubleSpinBox(), "mW")
		form_layout.addRow(self.laser_power)

		self.sample_length = FormCellUnits("Sample length:", QDoubleSpinBox(), "mm")
		form_layout.addRow(self.sample_length)

		self.aperture_transmittance = FormCellUnits("Aperture transmittance:", QDoubleSpinBox(), input_widget_value=0.01)
		form_layout.addRow(self.aperture_transmittance)

		form_layout.addRow(QLabel("Curve:"))

		calculate_layout = QHBoxLayout()
		form_layout.addRow(calculate_layout)

		self.calculate_button_group = QButtonGroup()
		
		calculate_sensor1 = QRadioButton("Sensor 1")
		calculate_sensor1.setStyleSheet("color: #FF0000; font-weight: bold")
		self.calculate_button_group.addButton(calculate_sensor1, 0)
		calculate_layout.addWidget(calculate_sensor1)

		calculate_sensor2 = QRadioButton("Sensor 2")
		calculate_sensor2.setStyleSheet("color: #0000FF; font-weight: bold")
		self.calculate_button_group.addButton(calculate_sensor2, 1)
		calculate_layout.addWidget(calculate_sensor2)

		form_layout.addRow(QLabel("Normalize curve with:"))

		normalize_layout = QHBoxLayout()
		form_layout.addRow(normalize_layout)

		self.normalize_button_group = QButtonGroup()
		
		normalize_sensor1 = QRadioButton("Sensor 1")
		normalize_sensor1.setStyleSheet("color: #FF0000; font-weight: bold")
		self.normalize_button_group.addButton(normalize_sensor1, 0)
		normalize_layout.addWidget(normalize_sensor1)

		normalize_sensor2 = QRadioButton("Sensor 2")
		normalize_sensor2.setStyleSheet("color: #0000FF; font-weight: bold")
		self.normalize_button_group.addButton(normalize_sensor2, 1)
		normalize_layout.addWidget(normalize_sensor2)

		normalize_far_field = QRadioButton("Far field")
		self.normalize_button_group.addButton(normalize_far_field, 2)
		normalize_layout.addWidget(normalize_far_field)

		layout.addLayout(form_layout)

		layout.addStretch()

		result_layout = QFormLayout()

		self.calculate_button = QPushButton("Calculate non-linear refraction index")
		self.calculate_button.clicked.connect(self.calculate_n2)
		result_layout.addRow(self.calculate_button)

		self.n2_label = QLabel(f"n₂ index: {self.n2}")
		self.n2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.n2_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
		result_layout.addRow(self.n2_label)

		layout.addLayout(result_layout)

	def load_file(self):
		path, _ = QFileDialog.getOpenFileName(self, "Open data file", '', "CSV Files (*.csv)")

		if not path:
			return
		
		try:
			loaded_df = pd.read_csv(path)

		except Exception as e:
			# TODO: Implement popup warning
			print(f"There was an error trying to read the file: {e}")
			return
		
		self.home_parent.plot_options.df = loaded_df

		def plot():
			self.home_parent.plot_options.doc.clear()
			create_new_plot(self.home_parent.plot_options.doc, self.home_parent, self.home_parent.options.move_from.input_widget.value(), self.home_parent.options.move_to.input_widget.value(), loaded_df)

		self.home_parent.plot_options.doc.add_next_tick_callback(plot)

	def calculate_n2(self):
		pan = 2.02547
		self.n2_label.setText(f"n₂ index: {pan}")