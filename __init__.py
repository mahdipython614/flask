from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from .app import book

test_config = None
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this in your code!

if test_config is None:
    app.config.from_mapping(secret_key="dev")
else:
    app.config.from_mapping(test_config)


@app.route('/', methods=['GET'])
def index():
    return {"message": "hello world"}


@app.errorhandler(404)
def error_404(e):
    print(e)
    return jsonify({'error': str(e)}), 404


@app.errorhandler(500)
def error_500(e):
    print(e)
    return jsonify({'error': str(e)}), 500


JWTManager(app)
app.register_blueprint(book)
