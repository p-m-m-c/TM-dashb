# Tom Misch dashboard via Last.fm data

# Load the API key
try:
    with open("api_key.txt", 'r') as file:
        api_key = file.readlines()[0]
    print("API key found and read")
except FileNotFoundError:
    print("File not found: configure API key correctly")

# Get the required data with the urllib library
import urllib3
import json
import datetime

root_url = "http://ws.audioscrobbler.com/2.0/"  # Root URL of Last.fm

http = urllib3.PoolManager()

request = http.request_encode_url(method='GET', url=root_url,
                                  fields={'method': 'artist.getinfo',
                                          'artist': 'Tom Misch',
                                          'format': 'json',
                                          'api_key': api_key})


data = json.loads(request.data.decode())

# Popularity -> {date: {listeners: x, playcount: y}}
popularity = {str(datetime.datetime.now().date()): data['artist']['stats']}

# On tour -> {0,1}
on_tour = data['artist']['ontour']

# Similar artists -> [artist1, artist2]
similar_artists = [item['name'] for item in data['artist']['similar']['artist']]

# Proceed with artist.getTopTracks, make new request and extract new data
# print(data['artist'].keys())
