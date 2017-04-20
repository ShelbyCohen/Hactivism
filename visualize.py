import plotly as plotly
import plotly.graph_objs as go
from plotly.graph_objs import *
from random import *
import os

plotly.tools.set_credentials_file(username='lanen', api_key='MocOzL15cD22AUbwdSSj')

def main () :
    print("creating plotly graphs...")
    path = "data/"
    item_path = path + "item/"
    file_path = os.path.dirname(item_path)

    movements = []
    similarities = [] #list of lists, where each sublist represents a row of 109 elements
    y = []
    for file in os.listdir(file_path):
        item_file = open(item_path + file, "r")
        for i, line in enumerate(item_file.readlines()):
            movements.append(line.strip("\n"))
            similarities.append([]) #new row
            for j in range (0, 109): #random number for each value, switch to cosine
                similarities[i].append(randint(0,100))
    print(similarities)

    trace = go.Heatmap(z= similarities, #lists of z values by row
                       x = movements, y = movements, colorscale = "Jet")
    data = [trace]
    plotly.offline.plot(data)


main()
