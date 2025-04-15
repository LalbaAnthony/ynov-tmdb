from flask import Flask, render_template, request, redirect, url_for
import requests
import os
import sqlite3
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

# ---------------------------
# Database Configuration & Wrapper Functions
# ---------------------------
DB_PATH = "media.db"

def get_db_connection():
    """Returns a new connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def create_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Drop the table if it exists so we recreate it with the new schema
    c.execute("DROP TABLE IF EXISTS media")
    c.execute('''
        CREATE TABLE media (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id INTEGER,
            media_type TEXT,
            title TEXT,
            original_title TEXT,
            release_date TEXT,
            overview TEXT,
            poster_path TEXT,
            vote_average REAL
        )
    ''')
    conn.commit()
    conn.close()

def clear_media():
    """Clear the media table."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM media")
    conn.commit()
    conn.close()

def insert_media(item):
    """Insert a single media item into the media table.
    
    item is a dict with keys: api_id, media_type, title, original_title, release_date, overview, poster_path, vote_average
    """
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO media (api_id, media_type, title, original_title, release_date, overview, poster_path, vote_average)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item['api_id'],
        item['media_type'],
        item['title'],
        item['original_title'],
        item['release_date'],
        item['overview'],
        item['poster_path'],
        item['vote_average'],
    ))
    conn.commit()
    conn.close()

def fetch_media(page=1, limit=20):
    """Fetch merged media records from the database with pagination."""
    conn = get_db_connection()
    c = conn.cursor()
    offset = (page - 1) * limit
    c.execute("""
        SELECT api_id, media_type, title, original_title, release_date, overview, poster_path, vote_average 
        FROM media 
        LIMIT ? OFFSET ?
    """, (limit, offset))
    rows = c.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "api_id": row[0],
            "media_type": row[1],
            "title": row[2],
            "original_title": row[3],
            "release_date": row[4],
            "overview": row[5],
            "poster_path": row[6],
            "vote_average": row[7]
        })
    return results

def fetch_suggestion(media_type=None, min_vote_average=None):
    """
    Récupère une suggestion (film ou série) depuis la base de données selon les critères.
    
    :param media_type: Filtrer par type ("movie" ou "tv"). Si None, on n'applique pas ce filtre.
    :param min_vote_average: Note minimale. Si None, aucun filtrage sur la note.
    :return: Un dictionnaire contenant les infos de suggestion ou None si introuvable.
    """
    conn = get_db_connection()
    c = conn.cursor()
    query = """
        SELECT api_id, media_type, title, original_title, release_date, overview, poster_path, vote_average 
        FROM merged_media 
        WHERE 1=1
    """
    params = []
    if media_type:
        query += " AND media_type = ?"
        params.append(media_type)
    if min_vote_average is not None:
        query += " AND vote_average >= ?"
        params.append(min_vote_average)
    query += " ORDER BY RANDOM() LIMIT 1"
    c.execute(query, params)
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "api_id": row[0],
            "media_type": row[1],
            "title": row[2],
            "original_title": row[3],
            "release_date": row[4],
            "overview": row[5],
            "poster_path": row[6],
            "vote_average": row[7]
        }
    else:
        return None


# ---------------------------
# API Wrapper Function
# ---------------------------
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
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {url}: {response.status_code}")
        return {"results": [], "total_pages": 0}

# ---------------------------
# API Functions (Extraction)
# ---------------------------
def get_popular_movies(page=1, genre_id=None):
    params = {"page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/movie/popular", params)

def get_now_playing_movies(page=1, genre_id=None):
    params = {
        "page": page,
        "region": "FR"  # Région France pour afficher les films en salle en France
    }
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/movie/now_playing", params)

def get_popular_tv_shows(page=1, genre_id=None):
    params = {"page": page}
    if genre_id:
        params["with_genres"] = genre_id
    return call_tmdb_api("/tv/popular", params)

def get_movie_genres():
    global movie_genres_cache
    if movie_genres_cache:
        return movie_genres_cache
    data = call_tmdb_api("/genre/movie/list")
    movie_genres_cache = data.get('genres', [])
    return movie_genres_cache

def get_tv_genres():
    global tv_genres_cache
    if tv_genres_cache:
        return tv_genres_cache
    data = call_tmdb_api("/genre/tv/list")
    tv_genres_cache = data.get('genres', [])
    return tv_genres_cache

def search_movies(query, page=1):
    params = {
        "query": query,
        "page": page
    }
    return call_tmdb_api("/search/movie", params)

# ---------------------------
# ETL Process: Extract, Transform, Load
# ---------------------------
def run_etl():
    """
    ETL process to fetch popular movies and TV shows from TMDB,
    merge them into a unified structure, and load them into the local database.
    """
    print("Starting ETL process...")
    # Create the database/table if not exist
    create_db()
    # Clear existing data in the media table
    clear_media()
    
    # Extract: Fetch popular movies and TV shows (first page for demonstration)
    movies_data = get_popular_movies(page=1)
    tv_data = get_popular_tv_shows(page=1)
    
    # Transform: Merge data with unified structure and add media_type field
    merged = []
    for movie in movies_data.get("results", []):
        merged.append({
            "api_id": movie.get("id"),
            "media_type": "movie",
            "title": movie.get("title"),
            "original_title": movie.get("original_title"),
            "release_date": movie.get("release_date"),
            "overview": movie.get("overview"),
            "poster_path": movie.get("poster_path"),
            "vote_average": movie.get("vote_average", 0)

        })
    for tv in tv_data.get("results", []):
        merged.append({
            "api_id": tv.get("id"),
            "media_type": "tv",
            "title": tv.get("name"),
            "original_title": tv.get("original_name"),
            "release_date": tv.get("first_air_date"),
            "overview": tv.get("overview"),
            "poster_path": tv.get("poster_path"),
            "vote_average": movie.get("vote_average", 0)
        })
    
    # Load: Insert merged data into the SQLite database
    for item in merged:
        insert_media(item)
    
    print("ETL process completed successfully.")

# ---------------------------
# Routes
# ---------------------------
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    
    if query:
        # When there's a query, use the API search results
        movies = search_movies(query, page)
        results = movies.get('results', [])
    else:
        # Otherwise, fetch the merged media from local SQLite DB
        results = fetch_media(page=page, limit=20)
    
    return render_template('index.html', 
                           movies=results, 
                           page=page, 
                           total_pages=1,  # Adjust total page count as needed
                           query=query,
                           image_base_url=IMAGE_BASE_URL,
                           active_page='home')

@app.route('/now-playing')
def now_playing():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    genres = get_movie_genres()
    
    movies = get_now_playing_movies(page, genre_id)
    
    return render_template('movie/movie_list.html', 
                           movies=movies.get('results', []), 
                           page=page, 
                           total_pages=movies.get('total_pages', 0),
                           image_base_url=IMAGE_BASE_URL,
                           genres=genres,
                           selected_genre=genre_id,
                           title="Films actuellement en salle",
                           endpoint='now_playing',
                           active_page='now_playing')

@app.route('/tv-shows')
def tv_shows():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    genres = get_tv_genres()
    
    tv_shows = get_popular_tv_shows(page, genre_id)
    
    return render_template('tv/tv_list.html', 
                           tv_shows=tv_shows.get('results', []), 
                           page=page, 
                           total_pages=tv_shows.get('total_pages', 0),
                           image_base_url=IMAGE_BASE_URL,
                           genres=genres,
                           selected_genre=genre_id,
                           title="Séries populaires",
                           endpoint='tv_shows',
                           active_page='tv_shows')

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    params = {"append_to_response": "credits,videos"}
    movie = call_tmdb_api(f"/movie/{movie_id}", params)
    if "results" not in movie or movie.get("id"):
        return render_template('movie/movie_detail.html', 
                               movie=movie, 
                               image_base_url=IMAGE_BASE_URL,
                               active_page='none')
    else:
        return "Film non trouvé", 404

@app.route('/tv/<int:tv_id>')
def tv_detail(tv_id):
    params = {"append_to_response": "credits,videos"}
    tv_show = call_tmdb_api(f"/tv/{tv_id}", params)
    if "results" not in tv_show or tv_show.get("id"):
        return render_template('tv/tv_detail.html', 
                               tv_show=tv_show, 
                               image_base_url=IMAGE_BASE_URL,
                               active_page='none')
    else:
        return "Série non trouvée", 

@app.route('/suggestion', methods=["GET", "POST"])
def suggestion():
    if request.method == "POST":
        # Récupération des critères envoyés par le formulaire
        media_type = request.form.get("media_type")
        # Si "both" est sélectionné, on ne filtre pas sur le media_type
        if media_type == "both":
            media_type = None
        min_vote = request.form.get("min_vote", type=float)
        suggestion = fetch_suggestion(media_type=media_type, min_vote_average=min_vote)
        return render_template("suggestion/suggestion_result.html", suggestion=suggestion, image_base_url=IMAGE_BASE_URL, active_page='suggestion')
    else:
        return render_template("suggestion/suggestion_form.html", active_page='suggestion')

# ---------------------------
# Main: Run ETL and start Flask server
# ---------------------------
if __name__ == '__main__':
    # Run the ETL process to update the local cache
    run_etl()
    # Start the Flask development server
    app.run(debug=True)
