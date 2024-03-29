# Tom Misch dashboard via Last.fm data

# Import the necessary libraries
import urllib3  # For making http requests
import json  # For parsing the json response
import os  # For checking files in directory
import sys  # To exit the script if it has already ran on a given day
import datetime as dt  # For checking and writing dates and times
import sqlalchemy as sa # For writing to database
import mysql # For connecting with mysql

# Print date for logging
print(dt.datetime.now())

# Add path prefix for execution from command line / cron
PATH_PREFIX = "/home/polpi/polpi/files/projects/TM-dashb/"

# Setup engine for MySQL db
eng = sa.create_engine('mysql+mysqlconnector://root:dbroot@localhost/TM_test')

# If script is already ran for today, don't run it again
tom_pop = sa.Table('Tom_pop', sa.MetaData(), autoload_with=eng)
q = sa.select([tom_pop]).order_by(sa.desc(tom_pop.columns.Date))
conn = eng.connect()
latest_date_in_db = str(conn.execute(q).first().Date.date())

if str(dt.datetime.now().date()) == latest_date_in_db:
    print('Thread exited: script already ran today')
    sys.exit(0)  # 0 indicates successful exited

# Load the API key
try:
    with open(PATH_PREFIX + "api_key.txt", 'r') as file:
        api_key = file.readlines()[0]
    print("API key found and read")
except FileNotFoundError:
    print("File not found: configure API key correctly")

ROOT_URL = "http://ws.audioscrobbler.com/2.0/"  # Root URL of Last.fm

HTTP = urllib3.PoolManager()


class artistInfoRequest:

    """
    Request class for a given artist.

    Valid artist name: any artist that appears in the Last.fm database
    Valid request types: {artist.getTopTracks, artist.getinfo}

    Methods:
    writing/fetching generic popularity data (write_popularity_data);
    writing/fetching top tracks to a csv (write_top_track_data);
    fetch similar artists to the specified artist.
    """

    def __init__(self, artist_name, request_type):

        assert request_type in ['artist.getInfo', 'artist.getTopTracks'], \
            """
            Provide valid request type. For examples, see
            https://www.last.fm/api/intro. Currently implemented ones include
            artist.getInfo (for generic play- and listener count) and
            artist.getTopTracks (for best tracks of artist)
            """

        self.artist_name = artist_name
        self.request_type = request_type
        self.initials = artist_name[:3]
        self.request = HTTP.request_encode_url(method='GET', url=ROOT_URL,
                                               fields={'method': self.request_type,
                                                       'artist': self.artist_name,
                                                       'format': 'json',
                                                       'api_key': api_key})

    def fetch_popularity_data(self):
        """
        Method of getInfo class. Fetches the data with a request to the API and structures the 
        required data into a dictionary that is written in the write_popularity_data method
        """
        try:
            data = json.loads(self.request.data.decode())

            data_dict = {'Date' : str(dt.datetime.now().date()),
                           'Listeners' : int(data['artist']['stats']['listeners']),
                           'Playcount' : int(data['artist']['stats']['playcount'])}
            return data_dict
        except:
            print("Encoding error: try different artist")

    def write_popularity_data(self):
        """
        Method of getInfo class. Takes the data fetched by the fetch_popularity_data method and 
        writes the data into MySQL database."""

        with eng.connect() as conn:
            track_table = sa.Table('Tom_pop', sa.MetaData(), autoload_with=eng)
            conn.execute(sa.insert(track_table, self.fetch_popularity_data()))

        print("Data written to track tbl")

    def fetch_similar_artists(self):
        try:
            data = json.loads(self.request.data.decode())

            similar_artists = [artist['name'] for artist in
                               data['artist']['similar']['artist']]

        except:
            print("Something went wrong in fetching similar artists")

    def fetch_top_track_data(self, n_top_tracks):
        """Method of topTrackRequest class. Fetches data with a request object
        from the API, then returns a list of tuples that is taken in by the
        write_top_track_data method for writing the data to the database."""

        data = json.loads(self.request.data.decode())

        track_popularity = [(item['name'], item['playcount'])
                            for item in data['toptracks']['track'] if
                            int(item['@attr']['rank']) <= n_top_tracks]

        return track_popularity

    def write_top_track_data(self):
        """Method of topTrackRequest class. It takes data via a
        topTrackRequest fetch method, then writes it to a MySQL database."""

        assert self.request_type == 'artist.getTopTracks', \
                                    "Use appropriate request type"

        list_of_track_tuples = self.fetch_top_track_data(n_top_tracks=5)

        value_list = [{'Date':str(dt.datetime.now().date()), 'Title':tup[0], 'Playcount':int(tup[1])} for tup in list_of_track_tuples]

        with eng.connect() as conn:
            track_pop_tbl = sa.Table('Tom_track_pop', sa.MetaData(), autoload_with=eng)
            conn.execute(sa.insert(track_pop_tbl, value_list))
        
        print("Data written to Tom_track_pop tbl")

# Get and write generic info
tom_misch_info_request = artistInfoRequest("Tom Misch", 'artist.getInfo')
tom_misch_info_request.write_popularity_data()


# Get and write top track info
tom_misch_tt_request = artistInfoRequest('Tom Misch', 'artist.getTopTracks')
tom_misch_tt_request.write_top_track_data()
