# app/models.py

from app.database import connection, does_db_exist, create_db

def clear_medias():
    conn = connection()
    c = conn.cursor()
    c.execute("DELETE FROM media")
    conn.commit()
    conn.close()

def clear_towatchs():
    conn = connection()
    c = conn.cursor()
    c.execute("DELETE FROM towatch")
    conn.commit()
    conn.close()

def insert_media(item):
    conn = connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO media (id, media_type, title, original_title, release_date, overview, poster_path, vote_average)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        item['id'],
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

def fetch_medias(media_type='both', page=1, now_playing=False):
    conn = connection()
    c = conn.cursor()
    
    limit=20
    offset = (page - 1) * limit

    params = []
    query = """
        SELECT id, media_type, title, original_title, release_date, overview, poster_path, vote_average  
        FROM media
        WHERE 1=1
    """
    if media_type:
        query += " AND media_type = ?"
        params.append(media_type)

    if now_playing:
        query += " AND release_date >= date('now')"

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
            "id": row[0],
            "media_type": row[1],
            "title": row[2],
            "original_title": row[3],
            "release_date": row[4],
            "overview": row[5],
            "poster_path": row[6],
            "vote_average": row[7]
        })

    return results

def fetch_media(id):
    conn = connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, media_type, title, original_title, release_date, overview, poster_path, vote_average  
        FROM media 
        WHERE id = ?
    """, (id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
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

def is_media_in_towatch(id):
    conn = connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, media_type
        FROM towatch 
        WHERE id = ?
    """, (id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return True
    else:
        return False

def insert_towatch(media):
    if is_media_in_towatch(media["id"]):
        print("Media already in towatch list. Skipping insert.")
        return True

    conn = None
    try:
        conn = connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO towatch (id, media_type, title, original_title, release_date, overview, poster_path, vote_average)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            media['id'],
            media['media_type'],
            media['title'],
            media['original_title'],
            media['release_date'],
            media['overview'],
            media['poster_path'],
            media['vote_average'],
        ))
        conn.commit()
        print("Insert successful.")
        return True
    except Exception as e:
        print("Error inserting media to towatch:", e)
    finally:
        if conn:
            conn.close()
        return False


def fetch_towatchs():
    conn = connection()
    c = conn.cursor()
    c.execute("""
        SELECT id, media_type, title, original_title, release_date, overview, poster_path, vote_average  
        FROM towatch 
    """)
    rows = c.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        results.append({
            "id": row[0],
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
    conn = connection()
    c = conn.cursor()
    query = """
        SELECT id, media_type, title, original_title, release_date, overview, poster_path, vote_average  
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
            "id": row[0],
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

def fill_db_from_tmdb(page=1):
    from app.tmdb import call_tmdb_api, get_movies, get_tv_shows, get_movie_detail, get_tv_show_detail, get_tv_genres, get_movie_genres, get_image_base_url
    print("Starting importing data from TMDB into media table...")

    if not does_db_exist(): 
        create_db()
        print("Database created successfully.")
    
    data_movies = get_movies()
    data_tv = get_tv_shows()

    # We need to clear the media table before inserting new data only if there is results
    if len(data_movies.get("results", [])) != 0 or len(data_tv.get("results", [])) != 0:
        clear_medias()
        print("media table cleared successfully.")      
        medias = []
        for movie in data_movies.get("results", []):
            medias.append({
                "id": movie.get("id"),
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
                "id": tv.get("id"),
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

    else :
        print("No data to insert into media table.")