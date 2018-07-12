# Tom Misch dashboard via Last.fm data

# Import the necessary libraries
import urllib3  # For making http requests
import json  # For parsing the json response
import os  # For checking files in directory
import sys  # To exit the script if it has already ran on a given day
import datetime as dt  # For checking and writing dates and times

# Print date for debugging
print(dt.datetime.now())

# Add path prefix for execution from command line / cron
PATH_PREFIX = "/home/polpi/polpi/files/projects/TM-dashb/"

# If script is already ran for today, don't run it again
with open(PATH_PREFIX + 'Tom_top_track_popularity.csv', mode='r') as f:
    lines = f.readlines()

if str(dt.datetime.now().date()) in lines[-1]:
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
        try:
            data = json.loads(self.request.data.decode())

            data_string = [str(dt.datetime.now().date()),
                           str(data['artist']['stats']['listeners']),
                           str(data['artist']['stats']['playcount'])]

            return (',').join(data_string)
        except:
            print("Encoding error: try different artist")

    def write_popularity_data(self):
        csv_name = PATH_PREFIX + self.initials + '_popularity_data.csv'

        if os.path.isfile(csv_name):
            mode = 'a'  # If file exists, append data
        else:
            mode = 'w'  # If file doesn't exist: create and write

        with open(csv_name, mode=mode) as f:
            f.write(self.fetch_popularity_data())
            f.write('\n')
        print("Data written to {}".format(csv_name))

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
        write_top_track_data method for writing the data to file."""

        data = json.loads(self.request.data.decode())

        track_popularity = [(item['name'], item['playcount'])
                            for item in data['toptracks']['track'] if
                            int(item['@attr']['rank']) <= n_top_tracks]

        return track_popularity

    def write_top_track_data(self):
        """Method of topTrackRequest class. It takes data via a
        topTrackRequest fetch method, then writes it to a csv."""

        assert self.request_type == 'artist.getTopTracks', \
                                    "Use appropriate request type"

        csv_name = PATH_PREFIX + self.initials + '_top_track_popularity.csv'
        if os.path.isfile(csv_name):
            mode = 'a'
        else:
            mode = 'w'

        try:
            with open(csv_name, mode=mode) as f:

                list_of_track_tuples = self.fetch_top_track_data(n_top_tracks=5)

                for tup in list_of_track_tuples:
                    f.write(str(dt.datetime.now().date()) + ',' +
                            tup[0] + ',' + tup[1])
                    f.write('\n')

            print('Data written to {}'.format(csv_name))

        except:
            print("Error in writing data to {}".format(csv_name))


# Get and write generic info
tom_misch_info_request = artistInfoRequest("Tom Misch", 'artist.getInfo')
tom_misch_info_request.write_popularity_data()


# Get and write top track info
tom_misch_tt_request = artistInfoRequest('Tom Misch', 'artist.getTopTracks')
tom_misch_tt_request.write_top_track_data()
