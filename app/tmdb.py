# app/services.py
import os
import requests
from dotenv import load_dotenv

# Charge l'environnement
load_dotenv()

API_SECRET = os.environ.get("API_SECRET")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def call_tmdb_api(endpoint, params=None):
    headers = {"Authorization": f"Bearer {API_SECRET}", "accept": "application/json"}
    default_params = {"language": "fr-FR"}
    if params:
        default_params.update(params)

    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=default_params)

    if response.status_code == 200:
        data = response.json()
        # Map 'id' to 'id'
        for item in data.get("results", []):
            item["id"] = item.pop("id", None)
        return data
    else:
        print(f"Error fetching {url}: {response.status_code}")
        return {"results": [], "total_pages": 0}    


def get_movies(search="", page=1, genre_id=None, now_playing=False):
    """
    Récupère une liste de films depuis l'API TMDB avec options de filtrage

    Args:
        search (str): Terme de recherche pour les films
        page (int): Numéro de page pour la pagination
        genre_id (int): Identifiant du genre pour filtrer les films
        now_playing (bool): Si True, récupère les films actuellement au cinéma

    Returns:
        dict: Données des films formatées
    """
    params = {"page": page}

    if now_playing:
        # Si now_playing est True, on utilise l'endpoint spécifique
        endpoint = "/movie/now_playing"
    elif search:
        # Si un terme de recherche est fourni, utiliser l'endpoint de recherche
        endpoint = "/search/movie"
        params["query"] = search
    else:
        # Sinon, récupérer les films populaires
        endpoint = "/discover/movie"
        params["sort_by"] = "popularity.desc"

    # Ajouter le filtre de genre si spécifié et si nous ne sommes pas sur l'endpoint now_playing
    if genre_id and endpoint != "/movie/now_playing":
        params["with_genres"] = genre_id

    # Si nous sommes sur l'endpoint now_playing et qu'un genre est spécifié,
    # nous devrons filtrer les résultats après avoir récupéré les données
    post_filter_by_genre = endpoint == "/movie/now_playing" and genre_id is not None

    data = call_tmdb_api(endpoint, params)

    # Formater les résultats pour inclure l'URL complète des images
    if "results" in data:
        # Filtrer les résultats par genre si nécessaire
        if post_filter_by_genre:
            filtered_results = []
            for movie in data["results"]:
                # Convertir en liste si nécessaire car les genres peuvent être un dictionnaire ou une liste d'ids
                movie_genres = movie.get("genre_ids", [])
                if isinstance(movie_genres, list) and genre_id in movie_genres:
                    filtered_results.append(movie)
            data["results"] = filtered_results

        # Ajouter l'URL complète pour les posters
        for movie in data["results"]:
            if movie.get("poster_path"):
                movie["poster_url"] = f"{IMAGE_BASE_URL}{movie['poster_path']}"
            else:
                movie["poster_url"] = None

        # Parse the name/title so tv shows and movies have the same format. Terrible hack but ya know
        for movie in data["results"]:
            if movie.get("original_title") and not movie.get("original_name"):
                movie["original_name"] = movie["original_title"]
            if movie.get("title") and not movie.get("name"):
                movie["name"] = movie["title"]

    return data


def get_tv_shows(search="", page=1, genre_id=None):
    """
    Récupère une liste de séries TV depuis l'API TMDB avec options de filtrage

    Args:
        search (str): Terme de recherche pour les séries
        page (int): Numéro de page pour la pagination
        genre_id (int): Identifiant du genre pour filtrer les séries

    Returns:
        dict: Données des séries formatées
    """
    params = {"page": page}

    if search:
        # Si un terme de recherche est fourni, utiliser l'endpoint de recherche
        endpoint = "/search/tv"
        params["query"] = search
    else:
        # Sinon, récupérer les séries populaires
        endpoint = "/discover/tv"
        params["sort_by"] = "popularity.desc"

    # Ajouter le filtre de genre si spécifié
    if genre_id:
        params["with_genres"] = genre_id

    data = call_tmdb_api(endpoint, params)

    # Formater les résultats pour inclure l'URL complète des images
    if "results" in data:
        for show in data["results"]:
            if show.get("poster_path"):
                show["poster_url"] = f"{IMAGE_BASE_URL}{show['poster_path']}"
            else:
                show["poster_url"] = None

    # Parse the name/title so tv shows and movies have the same format. Terrible hack but ya know
    for show in data["results"]:
        if show.get("original_name") and not show.get("original_title"):
            show["original_title"] = show["original_name"]
        if show.get("name") and not show.get("title"):
            show["title"] = show["name"]

    return data


def get_movie_detail(movie_id):
    """
    Récupère les détails d'un film spécifique depuis l'API TMDB

    Args:
        movie_id (int): Identifiant API du film

    Returns:
        dict: Données détaillées du film
    """
    endpoint = f"/movie/{movie_id}"
    params = {"append_to_response": "credits,videos,similar,recommendations"}

    data = call_tmdb_api(endpoint, params)

    # Formater les URLs des images
    if data.get("poster_path"):
        data["poster_url"] = f"{IMAGE_BASE_URL}{data['poster_path']}"
    else:
        data["poster_url"] = None

    if data.get("backdrop_path"):
        data["backdrop_url"] = (
            f"https://image.tmdb.org/t/p/original{data['backdrop_path']}"
        )
    else:
        data["backdrop_url"] = None

    # Remapper l'id pour être cohérent
    if "id" in data:
        data["id"] = data.pop("id")

    # Parse the name/title so tv shows and movies have the same format. Terrible hack but ya know
    if data.get("original_title") and not data.get("original_name"):
        data["original_name"] = data["original_title"]
    if data.get("title") and not data.get("name"):
        data["name"] = data["title"]

    return data


def get_tv_show_detail(show_id):
    """
    Récupère les détails d'une série TV spécifique depuis l'API TMDB

    Args:
        show_id (int): Identifiant API de la série

    Returns:
        dict: Données détaillées de la série
    """
    endpoint = f"/tv/{show_id}"
    params = {"append_to_response": "credits,videos,similar,recommendations,seasons"}

    data = call_tmdb_api(endpoint, params)

    # Formater les URLs des images
    if data.get("poster_path"):
        data["poster_url"] = f"{IMAGE_BASE_URL}{data['poster_path']}"
    else:
        data["poster_url"] = None

    if data.get("backdrop_path"):
        data["backdrop_url"] = (
            f"https://image.tmdb.org/t/p/original{data['backdrop_path']}"
        )
    else:
        data["backdrop_url"] = None

    # Traiter les saisons si présentes
    if "seasons" in data:
        for season in data["seasons"]:
            if season.get("poster_path"):
                season["poster_url"] = f"{IMAGE_BASE_URL}{season['poster_path']}"
            else:
                season["poster_url"] = None

            # Remapper l'id pour être cohérent
            if "id" in season:
                season["id"] = season.pop("id")

    # Remapper l'id pour être cohérent
    if "id" in data:
        data["id"] = data.pop("id")

    # Parse the name/title so tv shows and movies have the same format. Terrible hack but ya know
    if data.get("original_title") and not data.get("original_name"):
        data["original_name"] = data["original_title"]
    if data.get("title") and not data.get("name"):
        data["name"] = data["title"]

    return data


def get_tv_genres():
    result = call_tmdb_api("/genre/tv/list")
    if "genres" in result:
        return result["genres"]
    return []


def get_movie_genres():
    result = call_tmdb_api("/genre/movie/list")
    if "genres" in result:
        return result["genres"]
    return []


def get_image_base_url():
    return IMAGE_BASE_URL
