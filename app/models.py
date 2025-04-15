# app/models.py
import sqlite3

DB_PATH = "database.db"

def db_connection():
    """Returns a new connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def create_db():
    conn = db_connection()
    c = conn.cursor()
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
    c.execute("DROP TABLE IF EXISTS towatch")
    c.execute('''
        CREATE TABLE towatch (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_id INTEGER NOT NULL,
            media_type TEXT NOT NULL CHECK(media_type IN ('movie', 'tv')),
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

def clear_media():
    conn = db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM media")
    conn.commit()
    conn.close()

def clear_towatch():
    conn = db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM towatch")
    conn.commit()
    conn.close()

def insert_media(item):
    conn = db_connection()
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

def fetch_medias(media_type='both', page=1, limit=20):
    conn = db_connection()
    c = conn.cursor()
    offset = (page - 1) * limit

    params = []
    query = """
        SELECT api_id, media_type, title, original_title, release_date, overview, poster_path, vote_average 
        FROM media 
    """
    if media_type == 'movie':
        query += " WHERE media_type = 'movie'"
    elif media_type == 'tv':
        query += " WHERE media_type = 'tv'"
    else :
        query += " WHERE media_type IN ('movie', 'tv')"

    if limit and page:
        params.append(limit)
        params.append(offset)
        query += " LIMIT ? OFFSET ?"
    
    c.execute(query, params)
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

def insert_towatch(item):
    conn = db_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO towatch (api_id, media_type)
        VALUES (?, ?)
    """, (
        item['api_id'],
        item['media_type']
    ))
    conn.commit()
    conn.close()

def fetch_suggestion(media_type=None, min_vote_average=None):
    conn = db_connection()
    c = conn.cursor()
    query = """
        SELECT api_id, media_type, title, original_title, release_date, overview, poster_path, vote_average 
        FROM media 
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

def fill_media_from_tmdb(page=1):
    from app.tmdb import call_tmdb_api, get_movies, get_tv_shows, get_movie_detail, get_tv_show_detail, get_tv_genres, get_movie_genres, get_image_base_url
    print("Starting importing data from TMDB into media table...")

    create_db()
    
    data_movies = get_movies()
    data_tv = get_tv_shows()

    if len(data_movies.get("results", [])) == 0 and len(data_tv.get("results", [])) == 0:
            clear_media()

    medias = []
    for movie in data_movies.get("results", []):
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
    for tv in data_tv.get("results", []):
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