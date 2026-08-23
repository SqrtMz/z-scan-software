from serial import Serial
from serial.serialutil import SerialException
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd
from app.util.distance_conversions import steps_to_cm

def create_new_plot(doc, window, min_x_range=0, max_x_range=30, plot_data=None):
	r = BokehPlot(doc, window, min_x_range, max_x_range, plot_data)
	window.plot_options.set_bokeh_plot(r)

class BokehPlot:
	def __init__(self, doc, window, min_x_range=0, max_x_range=30, plot_data=None):

		self.doc = doc

		self.sources = [ColumnDataSource({'x': [], 'y': []}), ColumnDataSource({'x': [], 'y': []})]

		if plot_data is not None:
			self.sources[0].data = {'x': plot_data.iloc[:, 0].tolist(), "y": plot_data.iloc[:, 1].tolist()}
			self.sources[1].data = {'x': plot_data.iloc[:, 0].tolist(), "y": plot_data.iloc[:, 2].tolist()}

		self.p = figure(x_range = (min_x_range - 2 , max_x_range + 2), y_range=(-1000, 33000), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode input", tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"])
		self.p.toolbar.logo = None

		self.p.xaxis.axis_label_text_font_size = "12pt"
		self.p.yaxis.axis_label_text_font_size = "12pt"

		self.r1 = self.p.line(source=self.sources[0], color="red")
		self.r2 = self.p.line(source=self.sources[1], color="blue")

		def update(self):
			try:
				self.ser = Serial(window.device, 115200)

				data = self.ser.readline().decode("utf-8").strip()

				print(f"incoming: {data}")

				y1, y2, x = data.split(",")

			except (SerialException, ValueError) as e:
				window.plot_options.doc.remove_periodic_callback(window.plot_options.callback_id)
				window.plot_options.callback_id = None
				self.ser.close()
				print("There was an error while trying to read the data: " + str(e))
				# TODO: Implement popup warning
				window.statusBar().showMessage("Invalid device, please check the device selected")
				return

			x = steps_to_cm(int(x), window.options.distance_per_step)
			y1 = float(y1)
			y2 = float(y2)
			
			self.sources[0].stream({'x': [x], 'y': [y1]}, rollover=0)
			self.sources[1].stream({'x': [x], 'y': [y2]}, rollover=0)

			new_data = {
				'x': x,
				"y1": y1,
				"y2": y2
			}

			window.plot_options.plotted_data.append(new_data)

		window.plot_options.doc = doc
		window.plot_options.update_function = update

		window.options.plot = self.p
		
		doc.add_root(self.p)