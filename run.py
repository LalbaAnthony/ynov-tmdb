# run.py
from app import create_app
from app.services import run_etl

app = create_app()

if __name__ == '__main__':
    run_etl()  # Would ordinarily be run in a separate script, called by a cron job
    app.run(debug=True)
