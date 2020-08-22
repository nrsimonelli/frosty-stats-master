import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.figure_factory as ff

from data_puller import DataFormatter

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

USER = 'stbehiyxhmmfod'
PW = '66057c34fcb9944f7ad92a3ddfe169d03685d9f31deab60fe39b61a641a9e5de'
HOST = 'ec2-52-202-146-43.compute-1.amazonaws.com'
PORT = 5432
DB_NAME = 'd90jpcunrdd0f2'

data_formatter = DataFormatter(USER, PW, HOST, PORT, DB_NAME)
df_player_vs_opp = data_formatter.df_player_vs_opponent

# create win rate per pair fig
wr = round(data_formatter.create_wr_heatmap(), 2)
fig = ff.create_annotated_heatmap(wr.values,
                                  x=list(wr.index),
                                  y=list(wr.index),
                                  colorscale='rdbu',
                                  reversescale=True,
                                  font_colors=['black'])

# create games played per pair fig
counts = data_formatter.create_count_heatmap()
fig2 = ff.create_annotated_heatmap(counts.values,
                                   x=list(counts.index),
                                   y=list(counts.index),
                                   colorscale='Reds',
                                   reversescale=False)

app.layout = html.Div(children=[

    # div1
    html.Div([
        dcc.Dropdown(
            id='demo-dropdown',
            options=[
                {'label': 'Beef', 'value': 'Beef'},
                {'label': 'Charles', 'value': 'Charles'},
                {'label': 'Charlie', 'value': 'Charlie'},
                {'label': 'Ethan', 'value': 'Ethan'},
                {'label': 'Jagt', 'value': 'Jagt'},
                {'label': 'KJ', 'value': 'KJ'},
                {'label': 'Ryan', 'value': 'Ryan'},
                {'label': 'Simo', 'value': 'Simo'},
                {'label': 'Trevor', 'value': 'Trevor'},
                {'label': 'Connor', 'value': 'Connor'}
            ],
            value='Ryan',
            style=dict(
                width='50%',
                verticalAlign="left",
                display='inline-block')
        ),
        dcc.Graph(id='my_graph'),
    ], className='four columns'),

    # div2
    html.Div([
        html.H3('Total Games Played'),
        dcc.Graph(
            id='example-graph2',
            figure=fig2,
        ),
    ], className='four columns'),

    # div3
    html.Div([
        html.H3('Win %'),
        dcc.Graph(
            id='example-graph1',
            figure=fig,
        ),
    ], className='four columns'),

])


@app.callback(Output('my_graph', 'figure'), [Input('demo-dropdown', 'value')])
def update_graph(select_dropdown_value):
    df = df_player_vs_opp[df_player_vs_opp['player'] == select_dropdown_value].groupby('opponent')['win'].mean().sort_values()
    return {
        'data': [{
            'x': df.index,
            'y': df.values,
            'type': 'bar',
        }],
        'layout': {
            'title': f'{select_dropdown_value} Win Rate Against',
            'yaxis': {
                'range': [0, 1],
                'title': 'Win Rate',
                'nticks': 10,
                'showline': True,
                'showgrid': True,
                'mirror': 'ticks',

            }
        }

    }


if __name__ == '__main__':
    app.run_server(debug=True)
