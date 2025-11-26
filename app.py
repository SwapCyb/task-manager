from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import db, Task
import os

app = Flask(__name__, static_folder="static")
CORS(app)

# SQLite configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy with this app
db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()
    print("Database initialized at:", os.path.abspath("db.sqlite3"))

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# REST endpoints
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

# Serve frontend
@app.get("/")
def index():
    return send_from_directory("static", "index.html")

if __name__ == "__main__":
    app.run(debug=True)



