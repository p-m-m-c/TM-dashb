# Tom Misch dashboard via Last.fm data

# Load the API key
try:
    with open("api_key.txt", 'r') as file:
        api_key = file.read()
    print("API key found and read")
except FileNotFoundError:
    print("File not found: configure API key correctly")

# Get the required data with the urllib library
import urllib3
import json

root_url = "http://ws.audioscrobbler.com/2.0/"  # Root URL of Last.fm

http = urllib3.PoolManager()

request = http.request_encode_url(method='GET',
                                  url=root_url,
                                  fields={'method': 'artist.getinfo',
                                          'artist': 'Cher',
                                          'api_key': api_key,
                                          'format': 'json',
                                          'raw': 'true'})


print(request.data.decode('utf-8'))
