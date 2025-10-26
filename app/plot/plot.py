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

		source = ColumnDataSource({'x': [], 'y': []})

		p = figure(x_range = (min_x_range - 2 , max_x_range + 2), y_range=(0, 5000), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode Voltage (V)", tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"])
		p.toolbar.logo = None

		p.xaxis.axis_label_text_font_size = "12pt"
		p.yaxis.axis_label_text_font_size = "12pt"

		p.line(source=source, color="red")

		def update():
			try:
				ser = Serial(window.device, 115200)
				
				data = ser.readline(50).decode("utf-8").strip()

				print(data)

				y, x = data.split(",")
				ser.close()

			except (SerialException, ValueError):
				window.statusBar().showMessage("Invalid device, please check the device selected")
				window.plot_options.doc.remove_periodic_callback(window.plot_options.callback_id)
				window.plot_options.callback_id = None
				return

			x = steps_to_cm(int(x), window.options.distance_per_step)
			x = round(x, 3)
			
			source.stream({'x': [x], 'y': [y]}, rollover=0)

			new_data = {
				"x": x,
				"y": y
			}

			window.plot_options.df = pd.concat([window.plot_options.df, pd.DataFrame([new_data])], ignore_index=True)

		window.plot_options.doc = doc
		window.plot_options.update_function = update
		window.plot_options.callback_id = None
		window.options.plot = p
		
		doc.add_root(p)