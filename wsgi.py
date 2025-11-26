# wsgi.py
from app import app  # ensure app.py exposes `app = Flask(__name__)`
application = app    # Azure looks for "application" by default
