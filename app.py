from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
import builtins  # Importer le module builtins

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
                           image_base_url=IMAGE_BASE_URL)

# Obtenir les films populaires
def get_popular_movies(page=1):
    url = f"{BASE_URL}/movie/popular"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }
    params = {
        "language": "fr-FR",
        "page": page
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"results": [], "total_pages": 0}

# Rechercher des films
def search_movies(query, page=1):
    url = f"{BASE_URL}/search/movie"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }
    params = {
        "query": query,
        "language": "fr-FR",
        "page": page
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"results": [], "total_pages": 0}

# Détails d'un film
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "accept": "application/json"
    }
    params = {
        "language": "fr-FR",
        "append_to_response": "credits,videos"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        movie = response.json()
        return render_template('movie_detail.html', 
                               movie=movie, 
                               image_base_url=IMAGE_BASE_URL)
    else:
        return "Film non trouvé", 404

if __name__ == '__main__':
    app.run(debug=True)