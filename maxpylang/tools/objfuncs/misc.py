"""
.tools.obj.misc

Miscellaneous functions for the MaxObject class.

    notknown() --> check to see if the object has a reference file
    __str__(), __repr__() --> printing and rep of object, for info/debugging purposes

"""


from maxpylang.xlet import Inlet, Outlet

def notknown(self):
    """
    Return true if the object has no ref_file.
    """

    if self._ref_file == None:
        return True

    return False


#def isempty(self):
    #"""
    #Returns true if the object is empty; wrapper for notknown(), for clarity.
    #"""
    #return self.notknown()

def __repr__(self):

    rep = self.name + " ["
    if 'text' in self._dict['box'].keys():
        rep += self._dict['box']['text']
    else:
        rep += self._dict['box']['maxclass']

    rep += "]"

    return rep
