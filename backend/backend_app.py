from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

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


@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
