# TM-dashb
Dash application using Last.FM data about Tom Misch to be served from Ubuntu VM (e.g. via [DigitalOcean](https://www.digitalocean.com/))

### Functionality per file
#### Data_extraction_api.py
Data extraction script makes use of two classes; one for making requests and writing the results to a MySQL database on the same system about the artist, the second one is about the most popular tracks of the artist.

#### Dash_app.py
Reads the results from the MySQL database and makes some minor transformations using Pandas, then starts a Dash app that is served through the wsgi.py file.

#### Wsgi.py
Links the dash app to the gunicorn server that is finally able to expose the application on the IP address of the server.

### How to
- [Set up a MySQL database](https://www.digitalocean.com/community/tutorials/how-to-install-mysql-on-ubuntu-16-04) with a `root` account and password `dbroot` but make sure this accepts no ssh connections;
- Make sure the database is filled with some data before starting up the dash application, else there's no data to display;
- Install gunicorn and nginx and serve the applications as explained through [here](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04);
- Finally run `gunicorn --bind 0.0.0.0:5000 wsgi` to serve the application.
