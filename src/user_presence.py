from flask import Blueprint, request, jsonify
from sets import Set

blueprint = Blueprint('user_presence', __name__)

current_users = dict()

def add_user(location, user):
    if location not in current_users:
        current_users[location] = Set()
    current_users.add(user)

@blueprint.route('/current', methods=['GET'])
def get_users_endpoint():
    return jsonify(current_users)

@blueprint.route('/add', methods=['POST'])
def add_user_endpoint():
    add_user(request.form['location'] ,request.form['user'])
    current_users.add(user)
    return jsonify(current_users)

@blueprint.route('/remove', methods=['POST'])
def remove_user_endpoint():
    user = request.form['user']
    location = request.form['location']
    current_users[location].pop(user)
    return jsonify(current_users)