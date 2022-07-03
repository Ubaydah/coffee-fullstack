import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

@app.route('/')
def welcome():
    return jsonify({
        "status": "sucesss",
        "message": "Welcome to coffee shop"
        })

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()
    response = [drink.short() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": response
    }), 200

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drinks = Drink.query.all()
    response = [drink.long() for drink in drinks]

    return jsonify({
        "success": True,
        "drinks": response
    }), 200

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drinks(jwt):
    body = request.get_json()
    new_title = body['title']
    new_recipe = json.dumps(body["recipe"])

    try:
        drink = Drink(title=new_title, recipe=new_recipe)
        drink.insert()
        return jsonify({
                "success": True,
                "drinks": [drink.long()],
            }), 200
    
    except Exception as e:
        abort(422)

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(jwt, id):
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    body = request.get_json()

    if 'title' in body:
        drink.title = body['title']
    
    if 'recipe' in body:
        drink.recipe = json.dumps(body['recipe'])
    
    drink.update()

    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.get(id)
    id = drink.id
    if drink is None:
        abort(404)
    drink.delete()

    return jsonify({
        "success": True,
        "delete": id
    }), 200

# Error Handling
@app.errorhandler(AuthError)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": error.status_code,
        "message": error.error
        }), error.status_code

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
        }), 404

@app.errorhandler(500)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal Server Error"
        }), 500

@app.errorhandler(401)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 401,
        "message": "Unauthorized Request"
        }), 401

@app.errorhandler(403)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 403,
        "message": "Forbidden Request"
        }), 403

@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
        }), 400

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 405,
        "message": "Method not Allowed"
        }), 405