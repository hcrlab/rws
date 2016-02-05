from flask import Blueprint, request, jsonify
from subprocess import CalledProcessError
import config
import os
import rosnode
import secrets
import subprocess
import users
import yaml


class Robot(object):
    def __init__(self, blueprint, user_manager):
        self._blueprint = blueprint
        self._user_manager = user_manager
        self._blueprint.add_url_rule('/bringup', 'robot_bringup', self.bring_up,
                                     methods=['POST'])
        self._bring_up_launch = None

    def blueprint(self):
        return self._blueprint

    def is_brought_up(self):
        try:
            return True if '/robot_state_publisher' in rosnode.get_node_names(
            ) else False
        except:
            return False

    @users.login_required
    def bring_up(self):
        """Returns true if the robot was brought up, false if it was already up.
        """
        if not os.path.exists(secrets.BRINGUP_FILE):
            raise ValueError('Robot bringup file {} does not exist.'.format(
                secrets.BRINGUP_FILE))
        if self.is_brought_up():
            return jsonify({'isBroughtUp': False})
        self._bring_up_launch = subprocess.Popen(['roslaunch',
                                                  secrets.BRINGUP_FILE],
                                                 env=os.environ)
        return jsonify({'isBroughtUp': True})

    def bring_down(self):
        if self._bring_up_launch is None:
            return
        self._bring_up_launch.terminate()
        self._bring_up_launch.wait()
        self._bring_up_launch = None


class Pr2Claimer(object):
    def __init__(self, blueprint):
        self._blueprint = blueprint
        self._blueprint.add_url_rule('/claim', 'claim_robot', self.claim_robot,
                                     methods=['POST'])
        self._blueprint.add_url_rule('/start', 'start_robot', self.start_robot,
                                     methods=['POST'])
        self._blueprint.add_url_rule('/stop', 'stop_robot', self.stop_robot,
                                     methods=['POST'])
        self._blueprint.add_url_rule('/check', 'check_robot_claim',
                                     self.check_robot_claim)

    def blueprint(self):
        return self._blueprint

    @users.login_required
    def claim_robot(self):
        user = request.form['user']

        try:
            subprocess.check_call(
                'robot claim -f --username ' + user + ' --email ' + user +
                ' -m "Claimed via Robot Web Server"',
                shell=True)
        except CalledProcessError:
            return jsonify(
                {'status': 'error',
                 'message': 'Failed to claim robot.'})

        return jsonify({'status': 'success', 'message': 'Robot claimed.'})

    @users.login_required
    def start_robot(self):
        try:
            subprocess.check_call('robot start -f', shell=True)
        except CalledProcessError:
            return jsonify(
                {'status': 'error',
                 'message': 'Failed to start robot.'})

        return jsonify({'status': 'success', 'message': 'Robot started.'})

    @users.login_required
    def stop_robot(self):
        try:
            subprocess.check_call('robot stop -f', shell=True)
        except:
            return jsonify(
                {'status': 'error',
                 'message': 'Failed to stop robot.'})

        return jsonify({'status': 'success'})

    @users.login_required
    def check_robot_claim(self):
        active_user_file = config.ACTIVE_USER_FILE

        # if the active_user.yaml file exists, attempt to check claim
        if os.path.exists(active_user_file):
            try:
                fp = open(active_user_file, 'r')
                data = yaml.load(fp)

                return jsonify({'status': 'success', 'claim': data})
            except:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to check robot claim.'
                })

        # if the file doesn't exist, then the robot is not claimed
        else:
            return jsonify({
                'status': 'success',
                'message': 'Robot is not claimed currently.',
                'claim': None
            })
