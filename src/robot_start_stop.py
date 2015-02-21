from flask import Blueprint, request, jsonify
import subprocess
from subprocess import CalledProcessError
import os
import yaml

blueprint = Blueprint('robot_start_stop', __name__)

@blueprint.route('/claim', methods=['POST'])
@login_required
def claim_robot():
    user = request.form['user']

    try:
        subprocess.check_call('robot claim -f --username ' + user + ' --email ' + user + ' -m "teleoperating the robot (claimed via Robot Web Server)"', shell=True)
    except CalledProcessError:
        return jsonify({'status': 'error', 'message': 'Failed to claim robot.'})

    return jsonify({'status': 'success', 'message': 'Robot claimed.'})

@blueprint.route('/start', methods=['POST'])
@login_required
def start_robot():
    try:
        subprocess.check_call('robot start -f', shell=True)
    except CalledProcessError:
        return jsonify({'status': 'error', 'message': 'Failed to start robot.'})

    return jsonify({'status': 'success', 'message': 'Robot started.'})


@blueprint.route('/stop', methods=['POST'])
@login_required
def stop_robot():
    try:
        subprocess.check_call('robot stop -f', shell=True)
    except:
        return jsonify({'status': 'error', 'message': 'Failed to stop robot.'})

    return jsonify({'status': 'success'})

@blueprint.route('/check', methods=['GET'])
@login_required
def check_robot_claim():
    active_user_file = '/var/lib/robot/active_user.yaml'

    # if the active_user.yaml file exists, attempt to check claim
    if os.path.exists(active_user_file):
        try:
            fp = open(active_user_file, "r")
            content = fp.read()
            fp.close()
            data = yaml.load(content)
            
            return jsonify({
                'status': 'success',
                'claim': data
            })
        except:
            return jsonify({'status': 'error', 'message': 'Failed to check robot claim.'})

    # if the file doesn't exist, then the robot is not claimed
    else:
        return jsonify({
            'status': 'success',
            'message': 'Robot is not claimed currently.',
            'claim': None
        })