from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy

class FormCellUnits(QWidget):
	def __init__(self, label, input_widget, units, label_x_size=120, label_y_size=15, decimals=3, min_range=0, max_range=100000, update_value_function=lambda: None):
		super().__init__()

		self.main_layout = QHBoxLayout(self)
		self.main_layout.setContentsMargins(0, 0, 0, 0)

		self.label = QLabel(label)
		self.label.setFixedSize(label_x_size, label_y_size)

		self.input_widget = input_widget
		input_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
		input_widget.valueChanged.connect(update_value_function)

		if hasattr(input_widget, "setDecimals"):
			input_widget.setDecimals(decimals)

		if hasattr(input_widget, "setRange"):
			input_widget.setRange(min_range, max_range)

		self.units = QLabel(units)

		self.main_layout.addWidget(self.label)
		self.main_layout.addWidget(input_widget)
		self.main_layout.addWidget(self.units)

	def value(self):
		return self.input_widget.value()