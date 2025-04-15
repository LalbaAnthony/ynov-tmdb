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

def get_image_base_url():
    return IMAGE_BASE_URL
