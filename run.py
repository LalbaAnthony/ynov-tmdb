# run.py
from app import create_app
from app.models import fill_db_from_tmdb

app = create_app()

if __name__ == '__main__':
    fill_db_from_tmdb()  # Would ordinarily be run in a separate script, called by a cron job
    app.run(debug=True)
