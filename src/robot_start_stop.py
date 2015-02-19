from flask import Blueprint, request, jsonify
import subprocess
from subprocess import CalledProcessError
import os
import yaml

blueprint = Blueprint('robot_start_stop', __name__)

@blueprint.route('/start', methods=['POST'])
def claim_and_start_robot():
    user = request.form['user']

    try:
        subprocess.check_call('robot claim -f --username ' + user + ' --email ' + user + ' -m "teleoperating the robot (claimed via Robot Web Server)"', shell=True)
    except CalledProcessError:
        return jsonify({'status': 'error', 'message': 'failed to claim robot'})

    try:
        subprocess.check_call('robot start -f', shell=True)
    except CalledProcessError:
        return jsonify({'status': 'error', 'message': 'failed to start robot'})

    return jsonify({'status': 'success'})

@blueprint.route('/stop', methods=['POST'])
def stop_robot():
    try:
        subprocess.check_call('robot stop -f', shell=True)
    except:
        return jsonify({'status': 'error', 'message': 'failed to stop robot'})

    return jsonify({'status': 'success'})

@blueprint.route('/check', methods=['GET'])
def check_robot_claim():
    active_user_file = '/var/lib/robot/active_user.yaml'
    if os.path.exists(active_user_file):
        fp = open(active_user_file, "r")
        content = fp.read()
        fp.close()

        data = yaml.load(content)
        
        return jsonify({
            'status': 'success',
            'claim': data
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'active user file not found',
            'claim': None
        })