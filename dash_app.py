import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import pandas as pd
import sqlalchemy as sa

# Step 1: read in the data from MySQL database
eng = sa.create_engine('mysql+mysqlconnector://root:dbroot@localhost/TM_test') # Set up connection
pop_table = sa.Table('Tom_pop', sa.MetaData(), autoload=True, autoload_with=eng) # Create table object for popularity
track_table = sa.Table('Tom_track_pop', sa.MetaData(), autoload=True, autoload_with=eng) # Create table object for track popularity

# Define queries for data retrieval
retrieve_tom_pop_table = sa.select([pop_table])
retrieve_track_pop_table = sa.select([track_table])

# Execute the queries and store the results in pd DataFrames
with eng.connect() as conn:
    popularity_results = conn.execute(retrieve_tom_pop_table).fetchall()
    popularity_df = pd.DataFrame(popularity_results, columns=popularity_results[0].keys())
    track_results = conn.execute(retrieve_track_pop_table).fetchall()
    track_pop_df = pd.DataFrame(track_results, columns=track_results[0].keys()) 

# Construct grouped dataframes for further processing
gr_track_pop_df = track_pop_df.groupby(by='Title')['Playcount'].sum()
song_time_df = track_pop_df.groupby('Title')['Playcount', 'Date']

mapper = song_time_df.first()['Playcount'].to_dict() # Take playcount for every song on first observed date
track_pop_df['Base value'] = track_pop_df['Title'].map(mapper) # Map {title_song -> minimum value} in each row
track_pop_df['Playcount norm'] = (track_pop_df['Playcount'] / track_pop_df['Base value']) * 100 # Divide playcount by base value to obtain indices
song_time_df = track_pop_df.groupby('Title') # Redefine for plotting purposes

# Step 2: construct app and server
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
                                              y=song_time_df.get_group(song)['Playcount norm'],
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

server = app.server # Added for serving in production

# Only use these two lines for development purposes, not for production
#if __name__ == '__main__':

