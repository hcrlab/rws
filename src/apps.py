import os
import rospkg
import subprocess
import xml.etree.ElementTree as ET

# TODO(jstn): There is a code API for roslaunch:
# http://docs.ros.org/hydro/api/roslaunch/html/
# If we used it we could possibly use the process monitor to know when apps have
# failed. We could also possibly take advantage of their implementation of XML
# parsing. However, I think these aren't big enough advantages to justify
# rewriting this yet.


class AppManager(object):
    def __init__(self, catkin_ws=None, rosbuild_ws=None):
        self._catkin_ws = catkin_ws
        self._rosbuild_ws = rosbuild_ws

    def get_apps(self):
        """Traverses package directories for valid RWS apps.

        Returns a list of valid apps.
        """
        if self._catkin_ws is not None:
            full_paths = [p for p in rospkg.get_ros_paths() if p.startswith(self._catkin_ws)]
            app_list = []
            for path in full_paths:
                try:
                    app_list.append(App(path))
                except ValueError:
                    continue
            return app_list
        else:
            return []

    def close_all(self, apps):
        for app in apps:
            app.terminate()


class App(object):
    def __init__(self, path):
        self._package_path = path

        if not os.path.exists(os.path.join(path, 'launch', 'app.launch')):
            raise ValueError('Package {} has no app.launch'.format(path))

        package_xml_path = os.path.join(path, 'package.xml')
        if not os.path.exists(package_xml_path):
            raise ValueError('Package {} has no package.xml'.format(path))

        package_xml = ET.parse(package_xml_path)
        appname_elems = [x for x in package_xml.iter('appname')]
        if len(appname_elems) == 0:
            raise ValueError(
                'Package {} has no <appname> in package.xml'.format(path))
        self._name = appname_elems[0].text

        package_name_elems = [x for x in package_xml.iter('name')]
        if len(package_name_elems) == 0:
            raise ValueError(
                'Package {} has no <name> in package.xml'.format(path))
        self._package_name = package_name_elems[0].text

        self._subprocess = None

    def name(self):
        return self._name

    def package_name(self):
        return self._package_name

    def package_path(self):
        return self._package_path

    def is_running(self):
        return self._subprocess is not None

    def launch(self):
        # TODO(jstn): more thread safety stuff.
        if self._subprocess is None:
            launch_file = os.path.join(self._package_path, 'launch',
                                       'app.launch')
            if not os.path.exists(launch_file):
                return
            self._subprocess = subprocess.Popen(['roslaunch', launch_file],
                                                env=os.environ)

    def terminate(self):
        if self._subprocess is not None:
            self._subprocess.terminate()
        self._subprocess = None
