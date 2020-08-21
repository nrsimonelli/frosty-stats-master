import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff
import plotly.express as px
import pandas as pd
from graph_maker import HeatMapGraphMaker

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
map_maker = HeatMapGraphMaker('/Users/ryan.osgar/Documents/repos/frosty-stats-master/frosty-stats-master/mini_data.csv')
wr = map_maker.create_wr_heatmap()
wr = wr.applymap(lambda x: round(x, 2))

counts = map_maker.create_count_heatmap()
# counts_text = counts.applymap(lambda x: '{:.0f}'.format(x))

fig = ff.create_annotated_heatmap(wr.values,
                                  x=list(wr.index),
                                  y=list(wr.index),
                                  hovertext=counts.values,
                                  colorscale='rdbu',
                                  reversescale=True,
                                  font_colors=['black'])



fig2 = ff.create_annotated_heatmap(counts.values, x=list(counts.index), y=list(counts.index), colorscale='Reds', reversescale=False)


app.layout = html.Div(children=[

    html.Div([
        html.H3('Total Games Played'),
        dcc.Graph(
            id='example-graph2',
            figure=fig2,
            style={"height": "100%", "width": "100%"}
        ),
    ], className='six columns'),

    html.Div([
        html.H3('Win %'),
        dcc.Graph(
            id='example-graph1',
            figure=fig,
            style={"height": "100%", "width": "100%"}
        ),
    ], className='six columns')

])

if __name__ == '__main__':
    app.run_server(debug=True)
