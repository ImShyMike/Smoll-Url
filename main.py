"""Main module"""

import json
import random
import string
from datetime import datetime
from typing import Any

import validators
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    send_from_directory,
    request,
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app, default_limits=["5 per second"])

app.config["PORT"] = 8080
app.config["ID_LENGTH"] = 3
app.config["DATABASE_FILEPATH"] = "./redirects.json"


class RedirectBatabase:
    """Database for all redirects using a JSON file"""
    def __init__(self, filepath: str):
        self.filepath = filepath

        try:
            with open(filepath, "r", encoding="utf8") as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        self.data = data

    def __getitem__(self, key: str) -> Any:
        """Allow accessing items like a dictionary."""
        return self.data.get(key, None)

    def __setitem__(self, key: str, value: Any) -> None:
        """Allow setting items like a dictionary."""
        self.data[key] = value
        with open(self.filepath, "w", encoding="utf8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def __contains__(self, key: str) -> bool:
        """Check if the key exists in the database."""
        return key in self.data

db = RedirectBatabase(app.config["DATABASE_FILEPATH"])


def get_unique_id(database: RedirectBatabase) -> str:
    """Get an unique id using a database object"""
    while True:
        generated_id = "".join(
            random.choice(string.ascii_lowercase + string.digits)
            for _ in range(app.config["ID_LENGTH"])
        )
        if generated_id not in database:
            return generated_id


@app.errorhandler(404)
def page_not_found():
    """Page not found handler"""
    return render_template("404.html"), 404


@app.route("/", methods=["GET"])
def index():
    """Main page"""
    return render_template("index.html")


@app.route("/<redirect_id>", methods=["GET"])
def handle_redirect(redirect_id):
    """Handle redirects"""
    redirect_id = redirect_id.lower()
    if redirect_id in db:
        redirect_item = db[redirect_id]
        return redirect(redirect_item["url"], 301)
    return render_template("404.html")


@app.route("/create", methods=["POST"])
def handle_creation():
    """Handle creation of redirects"""
    data = request.json
    url = data.get("url")
    if url:
        if validators.url(url):
            redirect_id = get_unique_id(db)
            db[redirect_id] = {
                "url": url,
                "ip": request.remote_addr,
                "headers": request.headers.get("User-Agent"),
                "creation-time": datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
            }
            return jsonify({"id": redirect_id})
        return jsonify({"error": "Invalid url"}), 400
    return jsonify({"error": "Url not in POST data"}), 400

@app.route("/static/<path:path>", methods=["GET"])
def static_serve(path):
    """Serve a static file with caching"""
    response = make_response(send_from_directory("static", path))
    response.headers["Cache-Control"] = "public, max-age=54000"  # Add a 15 minute cache
    return response


@app.route("/favicon.ico", methods=["GET"])
def static_favicon():
    """Serve a the favicon with caching"""
    response = make_response(send_from_directory("static", "favicon.ico"))
    response.headers["Cache-Control"] = "public, max-age=54000"  # Add a 15 minute cache
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=app.config["PORT"], use_reloader=False)
