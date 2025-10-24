from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QGroupBox, QFileDialog
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineWidgets import QWebEngineView
import pandas as pd
from app.plot.plot import create_new_plot

class PlotSettings(QWidget):
	def __init__(self, home_parent):
		super().__init__()

		self.home_parent = home_parent
		self.doc = None
		self.update_function = None
		self.callback_id = None
		
		self.df = pd.DataFrame(columns=['x', 'y'])

		self.main_layout = QHBoxLayout(self)
		
		self.plot_group = QGroupBox("Plot")
		plot_layout = QVBoxLayout()
		self.plot_group.setLayout(plot_layout)
		self.main_layout.addWidget(self.plot_group)

		self.plot = QWebEngineView()
		self.plot.setUrl(f"http://localhost:5006/")
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

		path, _ = QFileDialog.getSaveFileName(self, "Save File As", "data.csv", "CSV Files (*.csv);; TXT Files (*.txt);; DAT Files (*.dat);; All Files (*)")

		if path:
			self.df.to_csv(path, index=False)

	def reset_plot(self):
		self.df = pd.DataFrame(columns=['x', 'y'])
		self.home_parent.settings.send_serial_command("reset_plot,")
		self.home_parent.settings.stop_data_collection()

		def clear():
			self.doc.clear()
			create_new_plot(self.doc, self.home_parent)
		
		self.doc.add_next_tick_callback(clear)