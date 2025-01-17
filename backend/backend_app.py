from flask import Flask, jsonify, request
from flask_cors import CORS
from blog_logic import BlogLogic, Index
from logger import setup_logger

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(app=app, key_func=get_remote_address)
CORS(app)
blog = BlogLogic()

logger = setup_logger(__name__)


POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

@app.before_request
def log_incoming_request():
    """ log incoming request info for security"""
    logger.info(f"Incoming  {request.method} from {request.remote_addr}")
@app.route('/')
def i_am_a_teacup():  # put application's code here
    return '', 418

@app.route('/api/posts', methods=['GET', 'POST'])
@limiter.limit("10/minute")
def get_posts():
    if request.method == "GET":
        search_pattern = request.args.get('title')
        #TODO add sort and direction functions
        sort = request.args.get('sort')
        direction = request.args.get('direction')

        if search_pattern:
            found_posts = blog.queried_posts(search_pattern=search_pattern)
            if found_posts:
                return jsonify(found_posts), 200
            else:
                return jsonify({"Error": f"No posts found matching {search_pattern}"}), 404
        else:
            return blog.posts, 200
    elif request.method == "POST":
        new_post = request.get_json()
        if blog.add_post(new_post):
            logger.info("New book added to persistent storage %s %s", new_post,
                        blog.posts)
            return jsonify({"book added": new_post['title']}), 201
        logger.warning("Invalid book data %s", new_post)
        return jsonify({"error": "Invalid book data"}), 400

@app.route("/api/delete/<int:id>", methods=['DELETE'])
def delete_post(id:Index):
    """delete post based on id"""
    post = blog.delete_post(id)
    if post:
        return jsonify({"{post['id']: {post['title']": "deleted"}), 200
    else:
        jsonify({"error": "Not Found"}), 404

@app.route("/api/posts/<int:id>", methods=['PUT'])
def update_post(id:Index):
    """update post based on index"""
    edited_post = request.get_json()
    updated_post = blog.update_post(post_id=id, edited_post= edited_post)
    if updated_post:
        return jsonify({f"{updated_post['id']}: {updated_post['title']}": "updated"}), 200
    else:
        jsonify({"error": "Not Found"}), 404





@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    return jsonify({"error": "Method Not Allowed"}), 405




if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
