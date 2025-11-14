import glob
import os
from pathlib import Path

"""
Miscellaneous helper functions.
"""


from maxpylang.tools.constants import obj_info_folder

def get_objs():
    """
    Fetches lists of all available (templated) objects, sorted into a dictionary by package.
    """

    #get all templated packages
    packages = glob.glob(os.path.join(obj_info_folder, "*/"))

    objs = {}
    for package_path in packages:

        #get package name
        package_name = os.path.basename(os.path.dirname(package_path))

        #get list of objects
        obj_path = os.path.join(package_path, "*.json")
        package_objs = sorted(glob.glob(obj_path))

        #get just the object name
        package_objs = [Path(x).stem for x in package_objs]

        #add to dict of available objects
        objs[package_name] = package_objs


    return objs
