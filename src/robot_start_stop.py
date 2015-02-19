from flask import Blueprint, request, jsonify
import subprocess

blueprint = Blueprint('robot_start_stop', __name__)

@blueprint.route('/start', methods=['POST'])
def claim_and_start_robot():
    user = request.form['user']

    result = subprocess.check_call('robot claim -f --username ' + user + ' --email ' + user + ' -m "teleoperating the robot (claimed via Robot Web Server)"', shell=True)
    if (result != 0):
        return jsonify({'status': 'error', 'message': 'failed to claim robot'})

    result = subprocess.check_call('robot start -f', shell=True)
    if (result != 0):
        return jsonify({'status': 'error', 'message': 'failed to start robot'})

    return jsonify({'status': 'success'})

@blueprint.route('/stop', methods=['POST'])
def stop_robot():
    result = subprocess.check_call('robot stop -f', shell=True)
    if (result != 0):
        return jsonify({'status': 'error', 'message': 'failed to stop robot'})

    return jsonify({'status': 'success'})

@blueprint.route('/check', methods=['GET'])
def check_robot_claim():
    if os.path.exists('/var/lib/robot/active_user.yaml'):
        fp = open(filename, "r")
        content = fp.read()
        fp.close()

        # TODO(csu): need to modify this, depending on how active_user.yaml is formatted
        return {
            'status': 'success',
            'claim': content
        }
    else:
        return {
            'status': 'error',
            'message': 'active user file not found',
            'claim': None
        }