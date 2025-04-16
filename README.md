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

### What happens if TMDB API is not available?

When the TMDB API is not available, we use a server side database to store the data.
Both movies and TV shows are stored in the same `media` table. We can retrieve either movies or TV shows by using the `media_type` field which can be either `movie` or `tv`. The `media` table contains as many fields as possible from the TMDB API. 

Database does not contains genres data of any kind. The filter feature is so disabled if the TMDB API is not available.

