# Reading and displaying the data creating a Dash app that runs on port 8080

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd

# Step 1: read in the data
popularity_df = pd.read_csv('Tom_popularity_data.csv')
track_pop_df = pd.read_csv('Tom_track_popularity.csv')

# Step 2: create the plotly figures
# add code..

# Step 3: create the dash app and insert plotly figures


app = dash.Dash()

app.layout = html.Div([
    html.H1("Norway car sales dash graphs"),

    dcc.Markdown("This graph shows yearly car sales in Norway"),

    dcc.Graph(id='graph1',
              figure={
                  "data": [{'x': df[df['Year'] == 2007]['Model'][:20],
                            'y': df[df['Year'] == 2007]['Quantity'][:20],
                            'type': 'bar', 'name': "2007"
                            },
                           {'x': df[df['Year'] == 2008]['Model'][:20],
                            'y': df[df['Year'] == 2008]['Quantity'][:20],
                            'type': 'bar', 'name': "2008"
                            }],
                  "layout": {"title": "Graph for 2007",
                             "xaxis": {"title": "Different models of years",
                                       "titlefont": {"size": 22}},
                             "yaxis": {"title": "QTY Sold"}
                             }
              })
]
)

if __name__ == '__main__':
    app.run_server(debug=True)
