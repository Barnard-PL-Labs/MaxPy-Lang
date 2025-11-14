"""
tools.obj.exposed

Functions of the MaxObject class that are exposed to the user. 

    edit() --> edit an object
    link() --> link a file for a js object or abstraction
    inspect() --> inspect an object

"""

import os

def move(self, x, y):
    """
    Move an object to the specified location. 
    """
    
    self._dict['box']['patching_rect'][0] = x
    self._dict['box']['patching_rect'][1] = y
    
    return

def edit(self, text_add = "append", text = None, **extra_attribs):
    """
    Edit an object by adding/replacing text and specifying attributes. 

    text_add --> 'append' : keep current args/text attributes, append specified args/text attributes
    text_add --> 'replace': erase current args/text attributes, replace with specified args/text attributes

    Should not use this function to change object class (i.e. name)!!!
    Can only change args/text attributes/extra attributes
    """

    #only edit if it's not an unknown object
    if self.notknown():
        print("Error: attempting edit on empty object")
        print("       nothing edited")
        return

    
    new_args = []
    new_text_attribs = {}

    #parse text if given
    if text is not None:
        if not text.startswith(self.name): #if missing name
            text = self.name + " " + text
        name, new_args, new_text_attribs = self.parse_text(text) #parse text

    #if appending, add new args/attribs to current args/attribs
    if text_add == "append":
        new_args = self._args + new_args
        new_text_attribs = self._text_attribs | new_text_attribs #will override overlapping attribs in favor of new

        
        
    #if it's an abstraction...
    if self._ref_file == "abstraction":
        
        #directly add new args/text_attribs w/o checking
        self._args = new_args
        self._text_attribs = new_text_attribs
        self.update_text()
        
        #add any extra attribs after checking against common attribs
        attrib_info = [{"name": "COMMON"}]
        x, extra_attribs = self.get_all_valid_attribs({}, extra_attribs, attrib_info)
        self.add_extra_attribs(extra_attribs) 
        
        #log abstraction edit and warn
        print("ObjectWarning:", self.name, ": edit :", "abstraction edited naively. if abstraction args " + \
              "affect inlets/outlets or abstraction has unique attributes, abstraction info must be imported " + \
              "using import_objs() function to reflect arg/attribute behaviors.")
        return
    

    #get obj info 
    info = self.get_info()

    #check args valid; if not, print error and don't edit
    if not self.args_valid(self.name, new_args, info['args']):
        print(self.name, "not edited")
        return
    self._args = new_args

    #get valid attribs
    self._text_attribs, extra_attribs = self.get_all_valid_attribs(new_text_attribs, extra_attribs, info['attribs'])


    #add or remove ins/outs based on arguments
    self.update_ins_outs(info['in/out'], info['default'])
    #add extra attributes to dict
    self.add_extra_attribs(extra_attribs)
    #update text box with name, args, text attribs
    self.update_text()

    return



def link(self, link_file=None):
    """
    Link a file for a js object or abstraction.
    
    link_file --> the filename, file MUST be placed in current directory
    link_file = None --> for js object with prev. given filename, will try to link that again
                     --> otherwise, won't work
    
    For js objects, linking or re-linking will automatically update the text field to reflect the proper filename.
    """
    
    #check for js file or abstraction or unknown (only three cases allowed)
    if not (self.name == "js" or self._ref_file is None or self._ref_file == 'abstraction'):
        print("ObjectError:", self.name, ": link : cannot be linked to a file")
        return
    
    #do linking for js file
    if self.name == 'js':  
        self.link_js(link_file=link_file)
    
    #or do linking for abstraction
    else:
        self.link_abstraction(link_file=link_file) 
    
    return


def inspect(self):
    """
    Print out specified information about the object. 
    """

    return