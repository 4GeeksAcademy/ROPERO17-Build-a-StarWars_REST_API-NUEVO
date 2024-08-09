"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200
@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def get_person(character_id):
    character = Character.query.get_or_404(character_id)
    return jsonify(character.serialize()), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get_or_404(planet_id)
    return jsonify(planet.serialize()), 200

#LISTAR USUARIOS
@app.route('/users',methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize()for user in users]), 200
#FAVORITOS DE USUARIOS
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1  
    user = User.query.get_or_404(current_user_id)
    favorites = {
        "planets": [planet.serialize() for planet in user.favorite_planet],
        "characters": [character.serialize() for character in user.favorite_character],
        "vehicles": [vehicle.serialize() for vehicle in user.favorite_vehicle],
    }
    return jsonify(favorites), 200
#PLANETA FAVORITO
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1  
    user = User.query.get_or_404(current_user_id)
    planet = Planet.query.get_or_404(planet_id)
    user.favorite_planet.append(planet)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites"}), 200
#PERSONAJE FAVORITO
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    current_user_id = 1  
    user = User.query.get_or_404(current_user_id)
    character = Character.query.get_or_404(people_id)
    user.favorite_character.append(character)
    db.session.commit()
    return jsonify({"msg": "Character added to favorites"}), 200
#BORRAR PLANETA FAVORITO
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1  
    user = User.query.get_or_404(current_user_id)
    planet = Planet.query.get_or_404(planet_id)
    if planet in user.favorite_planet:
        user.favorite_planet.remove(planet)
        db.session.commit()
        return jsonify({"msg": "Planet removed from favorites"}), 200
    return jsonify({"msg": "Planet not found in favorites"}), 404
#BORRAR PERSONAJE FAVORITO
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    current_user_id = 1  
    user = User.query.get_or_404(current_user_id)
    character = Character.query.get_or_404(people_id)
    if character in user.favorite_character:
        user.favorite_character.remove(character)
        db.session.commit()
        return jsonify({"msg": "Character removed from favorites"}), 200
    return jsonify({"msg": "Character not found in favorites"}), 404
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
