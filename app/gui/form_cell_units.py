from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy

class FormCellUnits(QWidget):
	def __init__(self, label, input_widget, units="", input_widget_value=0.0, label_x_size=175, label_y_size=15, units_x_size=30, units_y_size=15, decimals=3, min_range=0.0, max_range=100000.0, update_value_function=lambda: None):
		super().__init__()

		main_layout = QHBoxLayout(self)
		main_layout.setContentsMargins(0, 0, 0, 0)

		self.label = QLabel(label)
		self.label.setMinimumSize(label_x_size, label_y_size)

		self.input_widget = input_widget
		self.input_widget.setValue(input_widget_value)
		self.input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		self.input_widget.valueChanged.connect(update_value_function)

		if hasattr(self.input_widget, "setDecimals"):
			self.input_widget.setDecimals(decimals)

		if hasattr(self.input_widget, "setRange"):
			self.input_widget.setRange(min_range, max_range)

		main_layout.addWidget(self.label)
		main_layout.addWidget(self.input_widget)

		if units != "":
			self.units = QLabel(units)
			self.units.setAlignment(Qt.AlignmentFlag.AlignHCenter)
			self.units.setFixedSize(units_x_size, units_y_size)
			main_layout.addWidget(self.units)

	def value(self):
		return self.input_widget.value()