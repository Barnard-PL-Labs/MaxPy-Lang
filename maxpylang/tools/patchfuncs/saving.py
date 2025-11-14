"""
tools.patchfuncs.saving

Methods related to saving MaxPatches to files.

    save() --> save MaxPatch to file
    get_json() --> get json representation of MaxPatch
"""

import json
from pathlib import Path
import copy

#save patch to file
def save(self, filename="default.maxpat", verbose=True, check=True):

    """
    Save to .maxpat file.

    Usage:
    filename --> savefile name
    verbose --> print log message to console
    check --> run check_patch before saving
    """

    #check proper extension
    if ".maxpat" not in Path(filename).suffixes:
        filename += ".maxpat"

    #get json rep
    json_dict = self.get_json()

    #write json to file 
    with open(filename, 'w') as f:
        json.dump(json_dict, f, indent=2)
        
    #save filepath for later saving
    self._filename = filename
        
    #log unknown objs and unlinked js objs
    #(abstractions only get marked as abstractions if the file is found)
    #also log linked abstractions and linked js files 
    if check:
        self.check('unknown', 'js', 'abstractions')
            
    #log messages
    if verbose:
        print("maxpatch saved to", filename)


    return




def get_json(self):
    """
    Helper function for saving.

    Returns patcher dict with objects and patchcords added. 
    """

    #copy patcher_dict, for inserting objs and cords
    json_dict = copy.deepcopy(self._patcher_dict)

    #for each obj...
    for id, obj in self._objs.items():

        #add object jsons
        json_dict['patcher']['boxes'].append(obj._dict)

        #add patchcord json for outgoing edges...
        for outlet in obj.outs:
            #to each destination...
            for destination in outlet.destinations:
                #write patchcord going from id to destination.parent._dict['id']
                patchcord_dict = {'patchline':{'destination': [destination.parent._dict['box']['id'], destination.index],
                                               'source': [id, outlet.index], 
                                               'midpoints': destination.midpoints[destination.sources.index(outlet)]}}
                                                #midpoints entry corresponding to outlet entry, in source inlet 

                json_dict['patcher']['lines'].append(patchcord_dict)

    return json_dict