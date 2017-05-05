import plotly as plotly
import plotly.graph_objs as go
from plotly.graph_objs import *
import numpy as np

from random import *
import os

plotly.tools.set_credentials_file(username='lanen', api_key='MocOzL15cD22AUbwdSSj')


def main():
	print("creating plotly graphs...")
	path = "data/"
	item_path = path + "item/"
	file_path = os.path.dirname(item_path)

	movements = []
	similarities = []  # list of lists, where each sublist represents a row of 109 elements
	y = []
	for file in os.listdir(file_path):
		item_file = open(item_path + file, "r")
		for i, line in enumerate(item_file.readlines()):
			movements.append(line.strip("\n"))
			similarities.append([])  # new row
			for j in range(0, 87):  # random number for each value, switch to cosine
				similarities[i].append(randint(0, 100))
	print(similarities)

	trace = go.Heatmap(z=similarities,  # lists of z values by row
	                   x=movements, y=movements, colorscale="Jet")
	data = [trace]
	plotly.offline.plot(data)


def make_heatmap(cosine_list):
	print("creating plotly heatmap...")
	path = "data/"
	item_path = path + "item/"
	file_path = os.path.dirname(item_path)

	movements = []

	for file in os.listdir(file_path):
		item_file = open(item_path + file, "r")
		for i, line in enumerate(item_file.readlines()):
			movements.append(line.strip("\n"))

	trace = go.Heatmap(z=cosine_list,  # lists of z values by row
	                   x=movements, y=movements, colorscale="Jet")

	data = [trace]

	make_scatterplot(cosine_list, movements)
	plotly.offline.plot(data, filename='heatmap.html')

	return


def make_scatterplot(cosine_list, movement_list):
	print("creating plotly scatterplot...")
	movements = []
	queries = []
	x = list()
	y = list()
	z = list()
	colors = ["#004715", "#15302a", "#3c89a3", "#e2d9ff", "#443147", "#30011f", "#ffc7d9", "#e8898c", "#ffe9d9",
	          "#1a140d", "#a3990d", "#65752e", "#15a345", "#5e8c86", "#1a3347", "#276ee8", "#7725ba", "#e8e1e8",
	          "#a36286", "#75152c", "#75461c", "#a38a6a", "#fffa9e", "#65e823", "#69ffc8", "#e3fffb", "#03488c",
	          "#031130", "#3d125e", "#ff08d2", "#ff78b5", "#ba0b20", "#ff7e05", "#ffc663", "#ebff12", "#bae8ae",
	          "#087558", "#40ecff", "#63afff", "#130fff", "#c384e8", "#75095e", "#e81a62", "#300708", ]

	path = "data/"
	item_path = path + "item/"
	file_path = os.path.dirname(item_path)
	for file in os.listdir(file_path):
		item_file = open(item_path + file, "r")
		for i, line in enumerate(item_file.readlines()):
			movements.append(line.strip("\n"))

	traces = []
	for i in range(0, 108):  # go through movement list, where i is docID of query
		x.clear()
		y.clear()
		z.clear()
		for j in range(0, 108):  # j is docID of comparison docs
			x.append(movements[i])
			y.append(movements[j])
			if cosine_list[j][i] < 0.99:  # if they aren't the same document
				z.append(cosine_list[j][i])
			else:
				z.append(0)

		trace = Scatter3d(
			name=movements[i],
			x=x[:],
			y=y[:],
			z=z[:],
			mode='markers',
			marker=dict(
				size=5,
				color=colors[randint(0, len(colors) - 1)],  # choose a colorscale
				opacity=0.8
			)
		)

		traces.append(trace)
	layout = go.Layout(
		margin=dict(
			l=0,
			r=0,
			b=0,
			t=0
		)
	)

	data = Data(traces)

	fig = Figure(data=data, layout=layout)
	plotly.offline.plot(fig, filename='scatter_plot.html')
	return
