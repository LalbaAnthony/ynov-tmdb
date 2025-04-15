from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

app = Flask(__name__)

# Ajouter les fonctions builtin à Jinja2
app.jinja_env.globals.update({
    'max': max,
    'min': min
})

# Configuration de l'API
API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Cache pour les genres (pour éviter de les récupérer à chaque requête)
movie_genres_cache = None
tv_genres_cache = None

# API Wrapper Function to avoid repetition
def call_tmdb_api(endpoint, params=None):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }
    default_params = {
        "language": "fr-FR"
    }
    if params:
        default_params.update(params)
    
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=default_params)
    
    print(f"Fetching {url} with params {default_params}")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {url}: {response.status_code}")
        # Return a default value for list-based endpoints; detail endpoints will be checked later.
        return {"results": [], "total_pages": 0}

# Route principale
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    
    if query:
        movies = search_movies(query, page)
    else:
        movies = get_popular_movies(page)
    
    return render_template('index.html', 
                           movies=movies.get('results', []), 
                           page=page, 
                           total_pages=movies.get('total_pages', 0),
                           query=query,
                           image_base_url=IMAGE_BASE_URL,
                           active_page='home')

# Films actuellement en salle
@app.route('/now-playing')
def now_playing():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    genres = get_movie_genres()
    
    movies = get_now_playing_movies(page, genre_id)
    
    return render_template('movie_list.html', 
                           movies=movies.get('results', []), 
                           page=page, 
                           total_pages=movies.get('total_pages', 0),
                           image_base_url=IMAGE_BASE_URL,
                           genres=genres,
                           selected_genre=genre_id,
                           title="Films actuellement en salle",
                           endpoint='now_playing',
                           active_page='now_playing')

# Séries populaires
@app.route('/tv-shows')
def tv_shows():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    genres = get_tv_genres()
    
    tv_shows = get_popular_tv_shows(page, genre_id)
    
    return render_template('tv_list.html', 
                           tv_shows=tv_shows.get('results', []), 
                           page=page, 
                           total_pages=tv_shows.get('total_pages', 0),
                           image_base_url=IMAGE_BASE_URL,
                           genres=genres,
                           selected_genre=genre_id,
                           title="Séries populaires",
                           endpoint='tv_shows',
                           active_page='tv_shows')

# Obtenir les films populaires
def get_popular_movies(page=1, genre_id=None):
    params = {"page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/movie/popular", params)

# Obtenir les films actuellement en salle
def get_now_playing_movies(page=1, genre_id=None):
    params = {
        "page": page,
        "region": "FR"  # Région France pour afficher les films en salle en France
    }
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/movie/now_playing", params)

# Obtenir les séries populaires
def get_popular_tv_shows(page=1, genre_id=None):
    params = {"page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/tv/popular", params)

# Obtenir les genres de films
def get_movie_genres():
    global movie_genres_cache
    if movie_genres_cache:
        return movie_genres_cache
    data = call_tmdb_api("/genre/movie/list")
    movie_genres_cache = data.get('genres', [])
    return movie_genres_cache

# Obtenir les genres de séries
def get_tv_genres():
    global tv_genres_cache
    if tv_genres_cache:
        return tv_genres_cache
    data = call_tmdb_api("/genre/tv/list")
    tv_genres_cache = data.get('genres', [])
    return tv_genres_cache

# Rechercher des films
def search_movies(query, page=1):
    params = {
        "query": query,
        "page": page
    }
    return call_tmdb_api("/search/movie", params)

# Détails d'un film
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    params = {"append_to_response": "credits,videos"}
    movie = call_tmdb_api(f"/movie/{movie_id}", params)
    # Check if movie details exist by verifying if 'results' is not present
    if "results" not in movie or movie.get("id"):
        return render_template('movie_detail.html', 
                               movie=movie, 
                               image_base_url=IMAGE_BASE_URL,
                               active_page='none')
    else:
        return "Film non trouvé", 404

# Détails d'une série
@app.route('/tv/<int:tv_id>')
def tv_detail(tv_id):
    params = {"append_to_response": "credits,videos"}
    tv_show = call_tmdb_api(f"/tv/{tv_id}", params)
    if "results" not in tv_show or tv_show.get("id"):
        return render_template('tv_detail.html', 
                               tv_show=tv_show, 
                               image_base_url=IMAGE_BASE_URL,
                               active_page='none')
    else:
        return "Série non trouvée", 404

if __name__ == '__main__':
    app.run(debug=True)
