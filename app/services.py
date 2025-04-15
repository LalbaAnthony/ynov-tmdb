# app/services.py
import os
import requests
from dotenv import load_dotenv

# Charge l'environnement
load_dotenv()

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def call_tmdb_api(endpoint, params=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }
    default_params = {"language": "fr-FR"}
    if params:
        default_params.update(params)
    
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=default_params)
    
    if response.status_code == 200:
        data = response.json()
        # Map 'id' to 'api_id'
        for item in data.get("results", []):
            item["api_id"] = item.pop("id", None)
        return data
    else:
        print(f"Error fetching {url}: {response.status_code}")
        return {"results": [], "total_pages": 0}

def get_popular_movies(page=1, genre_id=None):
    params = {"page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/movie/popular", params)

def get_popular_tv_shows(page=1, genre_id=None):
    params = {"page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/tv/popular", params)

def run_etl(page=1):
    from app.models import create_db, clear_media, insert_media  # Import here to avoid circular imports
    print("Starting importing data from TMDB into media table...")
    create_db()
    clear_media()
    
    movies_data = get_popular_movies(page)
    tv_data = get_popular_tv_shows(page)
    
    medias = []
    for movie in movies_data.get("results", []):
        medias.append({
            "api_id": movie.get("api_id"),
            "media_type": "movie",
            "title": movie.get("title"),
            "original_title": movie.get("original_title"),
            "release_date": movie.get("release_date"),
            "overview": movie.get("overview"),
            "poster_path": movie.get("poster_path"),
            "vote_average": movie.get("vote_average", 0)
        })
    for tv in tv_data.get("results", []):
        medias.append({
            "api_id": tv.get("api_id"),
            "media_type": "tv",
            "title": tv.get("name"),
            "original_title": tv.get("original_name"),
            "release_date": tv.get("first_air_date"),
            "overview": tv.get("overview"),
            "poster_path": tv.get("poster_path"),
            "vote_average": tv.get("vote_average", 0)
        })
    
    for media in medias:
        insert_media(media)
    
    print("media insert completed successfully.")

def get_image_base_url():
    return IMAGE_BASE_URL
