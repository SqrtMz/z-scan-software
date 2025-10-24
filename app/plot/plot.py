from serial import Serial
from serial.serialutil import SerialException
from bokeh.models import ColumnDataSource, CustomAction, CustomJS
from bokeh.plotting import figure
import pandas as pd

def create_new_plot(doc, window):
	r = BokehPlot(doc, window)

class BokehPlot:
	def __init__(self, doc, window):

		source = ColumnDataSource({'x': [], 'y': []})

<<<<<<< Updated upstream
<<<<<<< Updated upstream
		p = figure(x_range = (0, 10000), y_range=(0, 5000), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode Voltage (V)")
=======
=======
>>>>>>> Stashed changes
		p = figure(x_range = (0, 100), y_range=(0, 5000), sizing_mode="stretch_both", x_axis_label="Distance (cm)", y_axis_label="Photodiode Voltage (V)", tools=["pan", "wheel_zoom", "box_zoom", "reset", "save"])
		p.toolbar.logo = None

		p.xaxis.axis_label_text_font_size = "12pt"
		p.yaxis.axis_label_text_font_size = "12pt"
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes

		p.scatter(source=source)
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