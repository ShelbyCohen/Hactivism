import plotly as plotly
import plotly.graph_objs as go
from plotly.graph_objs import *

plotly.tools.set_credentials_file(username='lanen', api_key='MocOzL15cD22AUbwdSSj')

def main () :
    
    trace = go.Heatmap(z=[[1, 20, 30, 50, 1], [20, 1, 60, 80, 30], [30, 60, 1, -10, 20]],
                       x=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
                       y=['Morning', 'Afternoon', 'Evening'])
    data = [trace]
    plotly.offline.plot(data)


main()
