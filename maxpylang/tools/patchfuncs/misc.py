"""
tools.patchfuncs.misc

Miscellaneous MaxPatch functions.
"""

def add_barebones_obj(self, obj_text):
    """
    For importing objs.
    Place a barebones obj in the patch. 
    """

    barebones_obj = {'box':{"maxclass":"newobj", "text": obj_text, "patching_rect": [100., 100.]}}

    self._patcher_dict['patcher']['boxes'].append(barebones_obj)

    return