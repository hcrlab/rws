import os
import xml.etree.ElementTree as ET

class AppManager(object):
  def __init__(self, catkin_ws=None, rosbuild_ws=None):
    self._catkin_ws = catkin_ws
    self._rosbuild_ws = rosbuild_ws

  def get_apps(self):
    """Traverses package directories for valid RWS apps.
    Returns a list of valid apps.
    """
    if self._catkin_ws is not None:
      # Assumes that apps are all packages and not metapackages.
      package_dir = os.path.join(self._catkin_ws, 'src')
      package_names = os.listdir(package_dir)
      full_paths = [os.path.join(package_dir, name) for name in package_names]
      return [App(path) for path in full_paths if self.is_valid_app(path)]
    else:
      return []

  def is_valid_app(self, path):
    # Must have an app.launch.
    if not os.path.exists(os.path.join(path, 'launch', 'app.launch')):
      return False

    # Must have <appname> element in package.xml exports. Catkin only.
    app_name = App.read_name(path)
    if app_name is None:
      return False

    return True

class App(object):
  def __init__(self, path):
    self._name = self.read_name(path)

  @staticmethod
  def read_name(path):
    package_xml_path = os.path.join(path, 'package.xml')
    if not os.path.exists(package_xml_path):
      return None
    package_xml = ET.parse(package_xml_path)
    appname_elems = [x for x in package_xml.iter('appname')]
    if len(appname_elems) != 1:
      return None
    return appname_elems[0].text

  def name(self):
    return self._name

  def launch(self):
    pass
