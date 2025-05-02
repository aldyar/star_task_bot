from uvicorn import run
from app.api import app

if __name__ == '__main__':
    run("app.api:app", host="0.0.0.0", port=5000, log_level="info")