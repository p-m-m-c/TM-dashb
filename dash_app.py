import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd

# Step 1: read in the data
popularity_df = pd.read_csv('Tom_popularity_data.csv', parse_dates=['Date'])
track_pop_df = pd.read_csv('Tom_top_track_popularity.csv', parse_dates=['Date'])
gr_track_pop_df = track_pop_df.groupby(by='Title')['Playcount'].mean()
song_time_df = track_pop_df.groupby('Title')

app = dash.Dash()
app.layout = html.Div([
    html.H1("Tom Misch Popularity: powered by Last.fm"),
    html.Div([
        html.Div([
            html.H3('Popularity - Total'),
            dcc.Graph(id='bar-chart-popularity',
                      figure={
                          "data": [go.Bar(x=['Listeners', 'Playcount'],
                                          y=[popularity_df['Listeners'].max(),
                                             popularity_df['Playcount'].max()],
                                          width=0.4,
                                          marker={'color': ['rgba(20,40,140,1)',
                                                            'rgba(23,124,60,1)']
                                                  })],
                          "layout": {"title": "Total listeners and Playcount",
                                     "xaxis": {"title": " ",
                                               "titlefont": {"size": 22}},
                                     "yaxis": {"title": "Number of listens/plays"}
                                     }
                      })], className="six columns"),
        # Add popularity donut chart
        html.Div([
            html.H3('Popularity - Songs'),
            dcc.Graph(id='pie-chart-songs',
                      figure={
                          "data": [go.Pie(labels=gr_track_pop_df.index,
                                          values=gr_track_pop_df.values,
                                          hole=0.4)],
                          "layout": {"title": "Popularity of songs"}
                      }
                      )], className="six columns"),
    ], className="row"),

    # Add time series for songs
    html.Div([
        html.H3('Song popularity over time - 2018'),
        dcc.Graph(id='line-chart-songs',
                  figure={"data": [go.Scatter(x=song_time_df.get_group(song)['Date'],
                                              y=song_time_df.get_group(song)['Playcount'],
                                              name=song,
                                              mode='lines') for song in list(song_time_df.groups.keys())],
                          "layout": {"title": "Song popularity over time",
                                     "xaxis": {"title": "Date",
                                               "tickangle": -45}}})
    ], className='row')
])

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

server = app.server

# Only use these two lines for development purposes, not for production
#if __name__ == '__main__':

