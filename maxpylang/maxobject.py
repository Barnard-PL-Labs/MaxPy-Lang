"""
Class representing a MaxObject.
"""


from .tools import misc


class MaxObject():

    #class variables
    arg_warning = True                              #flag to give argument warnings; can be turned off by user
    known_objs = misc.get_objs()                    #objs that have been templated
    from .tools.constants import common_box_attribs #common box attribs shared by non-ui objects
    from .tools.constants import obj_info_folder    #where to find the obj info
    from .tools.constants import unknown_obj_dict   #dictionary of unknown object


    def __init__(self, text, from_dict=False, **extra_attribs):

        """
        Initialize a MaxObject.

        from_dict = False --> initialize from in-box text (normal initialization in Max env)
            text --> in-box text
            extra_attribs --> attributes to change, formatted as attribute_name = val

        from_dict = True --> initialize from given json dict representation of obj (for loading in from existing file)
            text --> json dict
            extra_attribs --> not used

        """

        #instance vars
        self._ref_file = None      #reference file
        self._dict = None          #json rep
        self._name = None          #object name
        self._args = None          #only the args typed in-box
        self._text_attribs = None  #only includes attributes typed in-box
        self._ins = []             #list of Inlets
        self._outs = []            #list of Outlets
        self._ext_file = None      #external file, for js or abstraction

        if from_dict:
            self.build_from_dict(text)

        else:
            self.build_from_specs(text, extra_attribs)

        return


    #some properties...
    @property
    def name(self):
        """
        The name of the MaxObject, e.g. 'sel', 'bang', 'js'.
        """
        return self._name

    @property
    def ins(self):
        """
        A list of Inlet objects attached to the MaxObject.
        """
        return self._ins

    @property
    def outs(self):
        """
        A list of Outlet objects attached to the MaxObject.
        """
        return self._outs

    from .tools.objfuncs.exposed import move, edit, link, inspect #exposed functions for user use




    #************functions not meant for user use....

    #INSTANTIATION FUNCTIONS
    from .tools.objfuncs.instantiation import build_from_specs, build_from_dict



    #TEXT FUNCTIONS
    from .tools.objfuncs.text import parse_text, update_text, get_text



    #REF FILE FUNCTIONS
    from .tools.objfuncs.reffile import get_ref, check_aliases, get_info



    #FOR XLETS
    from .tools.objfuncs.makexlets import make_xlets_from_self_dict

    #update/add/remove xlets
    from .tools.objfuncs.makexlets import update_ins_outs, parse_io_num, add_xlets, remove_xlets, update_dict_io_nums

    #xlet typing
    from .tools.objfuncs.makexlets import update_xlet_typing, parse_io_typing


    #FOR ARGS
    from .tools.objfuncs.args import args_valid, get_typed_args



    #FOR ATTRIBS
    from .tools.objfuncs.attribs import add_extra_attribs, get_all_valid_attribs, \
                                        remove_bad_attribs, retain_attribs, get_extra_attribs



    #FOR SPECIAL OBJS
    from .tools.objfuncs.specialobjs import create_js, get_js_filename, get_js_io, update_js_from_file, link_js, \
                                            create_abstraction, get_abstraction_io, \
                                            update_abstraction_from_file, link_abstraction,  \
                                            get_trigger_out_types, get_unpack_out_types, update_vst



    #MISC FUNCTIONS
    from .tools.objfuncs.misc import notknown, __repr__


    #temporary debug
    def debug(self):
        print("ref_file", self._ref_file)
        print("dict", self._dict)
        print("name", self._name)
        print("args", self._args)
        print("text_attribs", self._text_attribs)
        print("ins", self._ins)
        print("outs", self._outs)
        print("ext_file", self._ext_file)

        return
