from serial import Serial
from serial.serialutil import SerialException
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
import pandas as pd
from app.util.distance_conversions import steps_to_cm

def create_new_plot(doc, window, min_x_range=0, max_x_range=30):
	r = BokehPlot(doc, window, min_x_range, max_x_range)

class BokehPlot:
	def __init__(self, doc, window, min_x_range=0, max_x_range=30):

		sources = [ColumnDataSource({'x': [], 'y': []}), ColumnDataSource({'x': [], 'y': []})]

		p = figure(x_range = (min_x_range - 2 , max_x_range + 2), y_range=(-1000, 33000), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode Voltage (V)", tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"])
		p.toolbar.logo = None

		p.xaxis.axis_label_text_font_size = "12pt"
		p.yaxis.axis_label_text_font_size = "12pt"

		r1 = p.line(source=sources[0], color="red")
		r2 = p.line(source=sources[1], color="blue")

		def update():
			try:
				self.ser = Serial(window.device, 115200, timeout=1)

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

			r1.visible = window.plot_options.sensor1.isChecked()
			r2.visible = window.plot_options.sensor2.isChecked()
			
			sources[0].stream({'x': [x], 'y': [y1]}, rollover=0)
			sources[1].stream({'x': [x], 'y': [y2]}, rollover=0)

			new_data = {
				"x": x,
				"y1": y1,
				"y2": y2
			}

			window.plot_options.plotted_data.append(new_data)

		window.plot_options.doc = doc
		window.plot_options.update_function = update
		window.plot_options.callback_id = None
		window.options.plot = p
		
		doc.add_root(p)