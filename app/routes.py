# app/routes.py
from flask import Blueprint, render_template, request, url_for
from app.tmdb import call_tmdb_api, get_movies, get_tv_shows, get_movie_detail, get_tv_show_detail, get_tv_genres, get_movie_genres, get_image_base_url
from app.models import fetch_suggestion, fetch_medias, fetch_media

main = Blueprint('main', __name__)

@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    genre_id = request.args.get('genre_id', None)

    movies = get_movies(search=query, page=page, genre_id=genre_id)
    genres = get_movie_genres()

    if not movies.get('results'):
        movies['results'] = fetch_medias('movie', page=page)
    
    return render_template(
        'index.html',
        movies=movies.get('results', []),
        page=page,
        genres=genres,
        total_pages=movies.get('total_pages', 0),
        query=query,
        genre_id=genre_id,
        image_base_url=get_image_base_url(),
        active_page='home',
        endpoint='main.index'
    )

@main.route('/now-playing')
def now_playing():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    genre_id = request.args.get('genre_id', None)

    movies = get_movies(search=query, page=page, genre_id=genre_id, now_playing=True)
    genres = get_movie_genres()

    if not movies.get('results'):
        movies['results'] = fetch_medias('movie', page=page, now_playing=True)

    return render_template(
        'movie/movie_list.html',
        movies=movies.get('results', []),
        page=page,
        genres=genres,
        total_pages=movies.get('total_pages', 0),
        query=query,
        genre_id=genre_id,
        image_base_url=get_image_base_url(),
        active_page='now_playing',
        endpoint='main.now_playing'
    )

@main.route('/movies')
def movies():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    genre_id = request.args.get('genre_id', None)

    movies = get_movies(search=query, page=page, genre_id=genre_id)
    genres = get_movie_genres()

    if not movies.get('results'):
        movies['results'] = fetch_medias('movie', page=page)

    return render_template(
        'movie/movie_list.html',
        movies=movies.get('results', []),
        page=page,
        genres=genres,
        total_pages=movies.get('total_pages', 0),
        query=query,
        genre_id=genre_id,
        image_base_url=get_image_base_url(),
        active_page='movies',
        endpoint='main.movies'
    )

@main.route('/tv-shows')
def tv_shows():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('query', '')
    genre_id = request.args.get('genre_id', None)

    tv_shows = get_tv_shows(search=query, page=page, genre_id=genre_id)
    genres = get_tv_genres()

    if not tv_shows.get('results'):
        tv_shows['results'] = fetch_medias('tv', page=page)

    return render_template(
        'tv/tv_list.html',
        tv_shows=tv_shows.get('results', []),
        page=page,
        genres=genres,
        total_pages=tv_shows.get('total_pages', 0),
        query=query,
        genre_id=genre_id,
        image_base_url=get_image_base_url(),
        active_page='tv-shows',
        endpoint='main.tv_shows'
    )

@main.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    
    movie = get_movie_detail(movie_id)

    if not movie:
        movie = fetch_media(movie_id)

    if "results" not in movie or movie.get("id"):
        return render_template(
            'movie/movie_detail.html',
            movie=movie,
            image_base_url=get_image_base_url(),
            active_page='none'
        )
    else:
        return "Film non trouvé", 404

@main.route('/tv/<int:tv_id>')
def tv_detail(tv_id):
    tv_show = get_tv_show_detail(tv_id)

    if not tv_show:
        tv_show = fetch_media(tv_id)

    if "results" not in tv_show or tv_show.get("id"):
        return render_template(
            'tv/tv_detail.html',
            tv_show=tv_show,
            image_base_url=get_image_base_url(),
            active_page='none'
        )
    else:
        return "Série non trouvée", 404

@main.route('/suggestion', methods=["GET", "POST"])
def suggestion():
    if request.method == "POST":

        media_type = request.form.get("media_type")
        if media_type == "both":
            media_type = None

        min_vote = request.form.get("min_vote", type=float)
        if min_vote is None:
            min_vote = 0

        suggestion = fetch_suggestion(media_type=media_type, min_vote_average=min_vote)
        return render_template(
            "suggestion/suggestion_result.html",
            suggestion=suggestion,
            image_base_url=get_image_base_url(),
            active_page='suggestion'
        )
    else:
        return render_template("suggestion/suggestion_form.html", active_page='suggestion')
