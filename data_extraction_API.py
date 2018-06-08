# Tom Misch dashboard via Last.fm data

# Get the required data with the urllib library
import urllib3
import json
import os
import sys
import datetime as dt

# If script is already ran for today, don't run it again
with open('Tom_top_track_popularity.csv', mode='r') as f:
    lines = f.readlines()

if lines[-1][:10] == str(dt.datetime.now().date()):
    print('Thread exited: script already ran today')
    sys.exit(0)  # 0 indicates successful exited

# Load the API key
try:
    with open("api_key.txt", 'r') as file:
        api_key = file.readlines()[0]
    print("API key found and read")
except FileNotFoundError:
    print("File not found: configure API key correctly")

ROOT_URL = "http://ws.audioscrobbler.com/2.0/"  # Root URL of Last.fm

HTTP = urllib3.PoolManager()


class artistInfoRequest:

    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.initials = artist_name[:3]

    def fetch_popularity_data(self):
        request = HTTP.request_encode_url(method='GET', url=ROOT_URL,
                                          fields={'method': 'artist.getinfo',
                                                  'artist': self.artist_name,
                                                  'format': 'json',
                                                  'api_key': api_key})
        try:
            data = json.loads(request.data.decode())

            data_string = [str(datetime.datetime.now().date()),
                           str(data['artist']['stats']['listeners']),
                           str(data['artist']['stats']['playcount'])]

            return (',').join(data_string)
        except:
            print("Encoding error: try different artist")

    def write_popularity_data(self):
        csv_name = self.initials + '_popularity_data.csv'

        if os.path.isfile('./' + csv_name):
            mode = 'a'  # If file exists, append data
        else:
            mode = 'w'  # If file doesn't exist: create and write

        with open(csv_name, mode=mode) as f:
            f.write(self.fetch_popularity_data())
            f.write('\n')
        print("Data written")

    def fetch_similar_artists(self):
        request = HTTP.request_encode_url(method='GET', url=ROOT_URL,
                                          fields={'method': 'artist.getinfo',
                                                  'artist': self.artist_name,
                                                  'format': 'json',
                                                  'api_key': api_key})
        try:
            data = json.loads(request.data.decode())
            similar_artists = [artist['name'] for artist in data['artist']['similar']['artist']]
        except:
            print("Something went wrong in fetching similar artists")


# Steps:
# 1: Instantiate request
tom_misch_artist_request = artistInfoRequest("Tom Misch")

# 2: Write and fetch popularity data
tom_misch_artist_request.write_popularity_data()


class topTrackRequest:

    """Request class for top tracks of a given artist. Methods are fetching top
    tracks (via fetch_top_track_data, five in total), and writing this data
    to a csv (write_top_track_data)."""

    def __init__(self, artist_name, n_top_tracks=5):
        self.artist_name = artist_name
        self.initials = artist_name[:3]
        self.n_top_tracks = n_top_tracks

    def fetch_top_track_data(self):
        """Method of topTrackRequest class. Fetches data with a request object
        from the API, then returns a list of tuples that is taken in by the
        write_top_track_data method for writing the data to file."""

        request = HTTP.request_encode_url(method='GET', url=ROOT_URL,
                                          fields={'method': 'artist.getTopTracks',
                                                  'artist': self.artist_name,
                                                  'format': 'json',
                                                  'api_key': api_key})

        data = json.loads(request.data.decode())

        track_popularity = [(item['name'], item['playcount'])
                            for item in data['toptracks']['track'] if
                            int(item['@attr']['rank']) <= self.n_top_tracks]

        return track_popularity

    def write_top_track_data(self):
        """Method of topTrackRequest class. It takes data via a
        topTrackRequest fetch method, then writes it to a csv."""

        csv_name = self.initials + '_top_track_popularity.csv'
        if os.path.isfile(csv_name):
            mode = 'a'
        else:
            mode = 'w'

        try:
            with open(csv_name, mode=mode) as f:

                list_of_track_tuples = self.fetch_top_track_data()

                for tup in list_of_track_tuples:
                    f.write(str(datetime.datetime.now().date()) + ',' +
                            tup[0] + ',' + tup[1])
                    f.write('\n')

            print('Data written to {}'.format(csv_name))

        except:
            print("Something went wrong in writing data to {}".format(csv_name))


# Instantiate request
tom_misch_tt_request = topTrackRequest(artist_name='Tom Misch', n_top_tracks=5)

# Write top track data
tom_misch_tt_request.write_top_track_data()
