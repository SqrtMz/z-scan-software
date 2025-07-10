from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QGroupBox, QFileDialog
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
from serial import Serial
from serial.serialutil import SerialException
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.driving import count
import pandas as pd

class PlotSettings(QWidget):
	def __init__(self):
		super().__init__()

		self.main_layout = QHBoxLayout(self)
		
		self.plot_group = QGroupBox("Plot")
		plot_layout = QVBoxLayout()
		self.plot_group.setLayout(plot_layout)
		self.main_layout.addWidget(self.plot_group)

		self.plot = QWebEngineView()
		self.plot.setUrl("http://localhost:5006/")
		plot_layout.addWidget(self.plot)
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


def update_plot(doc, window):

	source = ColumnDataSource({'x': [], 'y': []})

	p = figure(x_range=(-10, 100), y_range=(0, 1), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode Voltage (V)")

	p.scatter(source=source)
	p.line(source=source, color="red")

	@count()
	def update(x):

		try:
			ser = Serial(window.device, 115200)
			y = ser.readline(10)
			y = y.decode("utf-8").strip()
			ser.close()

		except SerialException:
			window.statusBar().showMessage("Invalid device, please check the device selected")
			window.doc.remove_periodic_callback(window.callback_id)
			window.callback_id = None
			return

		source.stream({'x': [x], 'y': [y]}, rollover=100)

		window.df = pd.concat([window.df, pd.DataFrame[source]], ignore_index=True)
		
		print(f"mcu value: {y}")

	window.doc = doc
	window.update_function = update
	window.callback_id = None
	
	doc.add_root(p)