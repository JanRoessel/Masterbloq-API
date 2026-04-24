from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)

SWAGGER_URL = "/api/docs"
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': 'Masterblog API'}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


def find_post(post_id):
    return next((p for p in POSTS if p["id"] == post_id), None)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    if sort_field:
        if sort_field not in ('title', 'content'):
            return jsonify({"error": "Invalid sort field. Must be 'title' or 'content'."}), 400
        if direction not in ('asc', 'desc'):
            return jsonify({"error": "Invalid direction. Must be 'asc' or 'desc'."}), 400

        return jsonify(sorted(POSTS, key=lambda p: p[sort_field].lower(), reverse=(direction == 'desc'))), 200

    return jsonify(POSTS), 200


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()

    missing_fields = [field for field in ("title", "content") if not data or not data.get(field)]
    if missing_fields:
        return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

    new_post = {
        "id": max((post["id"] for post in POSTS), default=0) + 1,
        "title": data["title"],
        "content": data["content"],
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    results = [
        post for post in POSTS
        if (title_query and title_query in post['title'].lower())
        or (content_query and content_query in post['content'].lower())
    ]

    return jsonify(results), 200


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = find_post(id)

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {id} has been deleted successfully."}), 200


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    post = find_post(id)

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    if data.get("title"):
        post["title"] = data["title"]

    if data.get("content"):
        post["content"] = data["content"]

    return jsonify(post), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)