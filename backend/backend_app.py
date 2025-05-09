from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL="/api/docs"
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)


app = Flask(__name__)
CORS(app)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET', 'POST'])
def get_posts():
    if request.method == 'POST':
        data = request.get_json()
        if not data.get('title') or not data.get('content'):
            return jsonify({"error": "Post must have a title and content"}), 400

        title = data.get('title')
        content = data.get('content')
        new_id = POSTS[-1]["id"] + 1
        POSTS.append({'id': new_id, 'title': title, 'content': content})

    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    if sort_field:
        if sort_field not in ['title', 'content']:
            return jsonify({"error": "Invalid sort field. Use 'title' or 'content'."}), 400
        if direction not in ['asc', 'desc']:
            return jsonify({"error": "Invalid direction. Use 'asc' or 'desc'."}), 400

        reverse = direction == 'desc'
        sorted_posts = sorted(POSTS, key=lambda post: post[sort_field].lower(), reverse=reverse)
        return jsonify(sorted_posts), 200

    return jsonify(POSTS), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_posts(post_id):
    global POSTS
    original_length = len(POSTS)
    POSTS = [post for post in POSTS if post['id'] != post_id]

    if len(POSTS) == original_length:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_posts(post_id):
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    post_found = False

    for post in POSTS:
        if post['id'] == post_id:
            post['title'] = title
            post['content'] = content
            post_found = True

    if not post_found:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    return jsonify(POSTS), 201


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    matching_posts = [
        post for post in POSTS
        if (title_query in post['title'].lower() if title_query else True) and
           (content_query in post['content'].lower() if content_query else True)
    ]

    return jsonify(matching_posts), 200


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
