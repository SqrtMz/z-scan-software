from serial import Serial
from serial.serialutil import SerialException
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.driving import count
import pandas as pd

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