from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db, bcrypt
from routes.auth import auth_bp
from routes.books import books_bp

app = Flask(__name__)
app.config.from_object(Config)

# CORS setup allows open API consumption without credential security blocks
CORS(app, resources={r"/api/*": {"origins": "*"}})

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(port=5000, debug=True)