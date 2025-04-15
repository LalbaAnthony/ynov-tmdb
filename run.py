# run.py
from app import create_app
from app.services import run_etl

app = create_app()

if __name__ == '__main__':
    run_etl()  # run ETL process before starting
    app.run(debug=True)
