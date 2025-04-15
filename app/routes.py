# app/routes.py
from flask import Blueprint, render_template, request, url_for
from app.tmdb import get_popular_movies, get_popular_tv_shows, get_image_base_url, call_tmdb_api
from app.models import fetch_media, fetch_suggestion
from app.tmdb import get_popular_movies  

main = Blueprint('main', __name__)

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    
    if query:
        from app.tmdb import call_tmdb_api
        movies_data = call_tmdb_api("/search/movie", {"query": query, "page": page})
        results = movies_data.get('results', [])
    else:
        results = fetch_media(page=page, limit=20)
        
    return render_template('index.html',
                           movies=results,
                           page=page,
                           total_pages=1,
                           query=query,
                           image_base_url=get_image_base_url(),
                           active_page='home')

@main.route('/now-playing')
def now_playing():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    movies_data = get_popular_movies(page, genre_id)
    return render_template('movie/movie_list.html',
                           movies=movies_data.get('results', []),
                           page=page,
                           total_pages=movies_data.get('total_pages', 0),
                           image_base_url=get_image_base_url(),
                           genres=[],   # add genres later
                           selected_genre=genre_id,
                           title="Films actuellement en salle",
                           endpoint='main.now_playing',
                           active_page='now_playing')

@main.route('/tv-shows')
def tv_shows():
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    tv_data = get_popular_tv_shows(page, genre_id)
    return render_template('tv/tv_list.html',
                           tv_shows=tv_data.get('results', []),
                           page=page,
                           total_pages=tv_data.get('total_pages', 0),
                           image_base_url=get_image_base_url(),
                           genres=[],  # add genres later
                           selected_genre=genre_id,
                           title="Séries populaires",
                           endpoint='main.tv_shows',
                           active_page='tv_shows')

@main.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    params = {"append_to_response": "credits,videos"}
    movie = call_tmdb_api(f"/movie/{movie_id}", params)
    if "results" not in movie or movie.get("api_id"):
        return render_template('movie/movie_detail.html',
                               movie=movie,
                               image_base_url=get_image_base_url(),
                               active_page='none')
    else:
        return "Film non trouvé", 404

@main.route('/tv/<int:tv_id>')
def tv_detail(tv_id):
    params = {"append_to_response": "credits,videos"}
    tv_show = call_tmdb_api(f"/tv/{tv_id}", params)
    if "results" not in tv_show or tv_show.get("api_id"):
        return render_template('tv/tv_detail.html',
                               tv_show=tv_show,
                               image_base_url=get_image_base_url(),
                               active_page='none')
    else:
        return "Série non trouvée", 404

@main.route('/suggestion', methods=["GET", "POST"])
def suggestion():
    if request.method == "POST":
        media_type = request.form.get("media_type")
        if media_type == "both":
            media_type = None
        min_vote = request.form.get("min_vote", type=float)
        suggestion = fetch_suggestion(media_type=media_type, min_vote_average=min_vote)
        return render_template("suggestion/suggestion_result.html",
                               suggestion=suggestion,
                               image_base_url=get_image_base_url(),
                               active_page='suggestion')
    else:
        return render_template("suggestion/suggestion_form.html", active_page='suggestion')
