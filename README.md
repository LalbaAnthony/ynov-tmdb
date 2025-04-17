# Ynov - TMDB API

## Quick start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

## API

The API is based on the TMDB API. You can find the documentation here:
https://developer.themoviedb.org/reference/intro/getting-started

## Project structure

- `template/`: This folder contains all the HTML templates used in the app. The main template is `base.html` which contains the header and footer of the app. The other templates are used to display the content of the app.
- `run.py`: This file is used to run the app. It contains the main function that runs the app and the routes that are used in the app.
- `tmdb.py`: This fill is used to interact with the TMDB API. All function use the `call_tmdb_api` function to call the TMDB API.
- `routes.py`: This file contains all the routes used in the app. It also contains some kind of controller that calls the functions in `tmdb.py` and `database.py` to get the data from the TMDB API or the database. All of those should really be in a `controller/` folder. 
- `database.py`: This file is used to interact with the database.
- `models.py`: This file contains main functions to interact 

### What happens if TMDB API is not available?

When the TMDB API is not available, we use a server side database to store the data.
Both movies and TV shows are stored in the same `media` table. We can retrieve either movies or TV shows by using the `media_type` field which can be either `movie` or `tv`. The `media` table contains as many fields as possible from the TMDB API.

Only the first page of the TMDB API is stored in the database to avoid too long booting time.
Database does not contains genres data of any kind. The filter feature is so disabled if the TMDB API is not available.

### What happens if the server database is not available?

All watch list data is first stored in the local storage. Then it is sent to the server when it is available. 5 tries are made to send the data to the server. If the server is still not available, the data is stored in the local storage until the server is available again. The data is then sent to the server and removed from the local storage.
This part is in the `<script>` tab of `base.html`.
