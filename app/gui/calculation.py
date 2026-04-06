from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFormLayout, QDoubleSpinBox, QGroupBox, QSizePolicy, QPushButton, QLabel, QVBoxLayout, QSpacerItem, QHBoxLayout
from app.gui.form_cell_units import FormCellUnits

class Calculation(QGroupBox):
	def __init__(self):
		super().__init__()

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

		self.calculate_button = QPushButton("Calculate non-linear refraction index")
		form_layout.addRow(self.calculate_button)

		layout.addLayout(form_layout)

		layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

		result_layout = QFormLayout()
		self.n2_label = QLabel(f"n₂ index: {self.n2}")
		self.n2_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
		result_layout.addRow(self.n2_label)

		layout.addLayout(result_layout)