import os
import logging
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Task

# Configure logging
logging.basicConfig(level=logging.INFO)

# Read Weather API key from environment
OWM_API_KEY = os.getenv("OWM_API_KEY", "")

# Initialize Flask app
app = Flask(__name__, static_folder="static")
CORS(app)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()
    app.logger.info("Database initialized at: %s", os.path.abspath("db.sqlite3"))

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# REST endpoints for tasks
@app.get("/tasks")
def get_tasks():
    tasks = Task.query.all()
    return jsonify([t.to_dict() for t in tasks])

@app.post("/tasks")
def create_task():
    data = request.get_json(force=True)
    title = data.get("title")
    description = data.get("description")
    status = data.get("status", "pending")

    if not title:
        return jsonify({"error": "title is required"}), 400

    task = Task(title=title, description=description, status=status)
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201

@app.put("/tasks/<int:task_id>")
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.get_json(force=True)
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.status = data.get("status", task.status)
    db.session.commit()
    return jsonify(task.to_dict())

@app.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"deleted": task_id})

# Weather endpoint
@app.get("/weather")
def weather():
    city = (request.args.get("city") or "").strip()
    if not city or not OWM_API_KEY:
        return jsonify({"error": "city or key missing"}), 400

    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": OWM_API_KEY, "units": "metric"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return jsonify(data)
    except requests.RequestException as e:
        app.logger.error("Weather API error: %s", e)
        return jsonify({"error": "failed to fetch weather"}), 500

# Serve frontend
@app.get("/")
def index():
    return send_from_directory("static", "index.html")

# Entry point for Azure
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
