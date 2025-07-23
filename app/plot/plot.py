from serial import Serial
from serial.serialutil import SerialException
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.driving import count
import pandas as pd

def create_new_plot(doc, window):
	r = BokehPlot(doc, window)

class BokehPlot:
	def __init__(self, doc, window):

		source = ColumnDataSource({'x': [], 'y': []})

		p = figure(x_range = (0, 100), y_range=(0, 5000), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode Voltage (V)")

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
				window.plot_settings.doc.remove_periodic_callback(window.plot_settings.callback_id)
				window.plot_settings.callback_id = None
				return

			source.stream({'x': [x], 'y': [y]}, rollover=100)

			new_data = {
				"x": x,
				"y": y
			}

			window.plot_settings.df = pd.concat([window.plot_settings.df, pd.DataFrame([new_data])], ignore_index=True)

		window.plot_settings.doc = doc
		window.plot_settings.update_function = update
		window.plot_settings.callback_id = None
		
		doc.add_root(p)