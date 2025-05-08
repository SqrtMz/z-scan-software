from serial import Serial
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from bokeh.driving import count

def update_plot(doc, window):

	source = ColumnDataSource({'x': [], 'y': []})

	p = figure(y_range=(-300, 4500), width=400, height=400)

	p.scatter(source=source)
	p.line(source=source, color="red")

	@count()
	def update(x):

		ser = Serial(window.device, 115200)
		y = ser.readline(10)
		y = y.decode("utf-8").strip()
		ser.close()

		source.stream({'x': [x], 'y': [y]}, rollover=100)
		
		print(f"mcu value: {y}")

	window.doc = doc
	window.update_function = update
	window.callback_id = None
	
	doc.add_root(p)