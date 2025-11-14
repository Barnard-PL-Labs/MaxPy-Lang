import numpy as np
import os
import json
import glob
from pathlib import Path
import shutil
import subprocess
import time
import xml.etree.ElementTree as ET
import collections


#import some constants...
from .tools.constants import get_constant
from .tools.constants import obj_info_folder   #path to maxpy obj info folder
from .tools.constants import obj_io_folder     #path to obj io folder
from .tools.constants import import_tools      #maxpatch json to add open/close functionality 

from .maxpatch import MaxPatch

#other constants
common_box_standin = [{'name': 'COMMON'}] #for attributes 
available_argtypes = ['int', 'symbol', 'number', 'list', 'any', 'float'] #for arguments
known_aliases = {'t':'trigger', 'sel': 'select', 'b': 'bangbang'} #known aliases


def import_objs(*packages, overwrite=False):
    """
    Import objects from MaxMSP packages for compatibility with Python interface.
    Creates object template files.
    
    Requires io files for each package describing the relationship between inlets/outlets and arguments.
    
    Usage:
    input --> list of package folder names, use keyword "vanilla" as shortcut for [max, msp, jit]. 
    overwrite --> flag to re-import previously imported objects 
    
    Make sure the Max application is OPEN when running this command!
    If import fails, set wait_time higher and re-import. 
    """
    
    #create obj_info_folder to hold ref_files
    if not os.path.exists(obj_info_folder):
        os.mkdir(obj_info_folder)

    
    #get paths to Max ref files 
    package_paths = get_package_paths(list(packages))
    
    #create maxpy info folder for each package
    package_info_folders = prep_make_info_folders(package_paths, overwrite=overwrite)
    
    #store object info
    save_obj_info(package_paths, package_info_folders)
    
    return 



#############################################################################################
########      SHOULD BE PRIVATE FUNCTIONS       #############################################
#############################################################################################


#************************************************************
#*************** FILE PATH STUFF ****************************
#************************************************************

def get_package_paths(packages):
    """
    Gets paths to the Max reference directories for each package in specified list.
    """
    vanilla_refpath = get_constant('max_refpath')
    packages_refpath = get_constant('packages_path')
    
    package_paths = {}
    
    for package in packages:
        
        #add max, msp, jit if vanilla 
        if package == 'vanilla':
            packages.append('max')
            packages.append('msp')
            packages.append('jit')
            
        #add vanilla path for max, msp, jit
        elif package == 'max' or package == 'msp' or package == 'jit':
            package_paths[package] = os.path.join(vanilla_refpath, package + "-ref")
            
        #add from package path for all others
        else:
            package_paths[package] = os.path.join(packages_refpath, package + "/docs")
            
    return package_paths



def prep_make_info_folders(package_paths, overwrite=False):
    
    """
    Makes maxpy info folders for packages specified.
    
    Checks for package existance, deletes old folder if overwriting, makes new folder if new import.
    """
    
    package_info_folders = {}
    for package, package_path in package_paths.items():
        
        #check to see if package exists
        if not os.path.exists(package_path):
            print("package", package, "not found")
            
        else:
        
            #make path for package info folder
            package_info_folder = os.path.join(obj_info_folder, package)

            #if prev. imported and not overwriting, skip import
            if os.path.exists(package_info_folder) and not overwrite:
                print(package, "previously imported, skipping...")

            else:
                #otherwise, import
                
                #remove old folder if necessary
                if os.path.exists(package_info_folder): #package prev imported, overwriting
                    print("prepping to re-import", package, "...")
                    shutil.rmtree(package_info_folder) #remove old folder
                else:
                    print("prepping to import", package, "...") #package importing for first time

                #create new folder
                os.mkdir(package_info_folder)

                #add to dictionary
                package_info_folders[package] = package_info_folder
           
    print()
    print(len(package_info_folders), "package(s) prepped, ready for import\n")
    
    return package_info_folders


#************************************************************
#*************** FOR SAVING OBJECT INFO *********************
#************************************************************

def save_obj_info(package_paths, package_info_folders):
    """
    Saves default, argument, attribute, and inlet/outlet info for each object in the specified packages.
    Also saves obj aliases into obj_aliases.json file. 
    """
    
    obj_aliases = known_aliases
    
    #store object info, by package
    for package, info_folder in package_info_folders.items():
        
        print("importing", package, "objects...") #log
       
        ref_folder = package_paths[package] #max refs folder
        obj_refs = sorted(glob.glob(os.path.join(ref_folder, "*.maxref.xml"))) #get all object reffiles
        obj_refs = [ref for ref in obj_refs if not is_unlisted(ref)] #remove unlisted objects 
        obj_names = [Path(Path(x).stem).stem for x in obj_refs] #get object names 
        
        #get default obj info (dict for default instantiation)
        print("\tgetting defaults...")
        default_obj_info = get_default_obj_info(package, obj_refs, obj_names)
        print("\tdefaults retrieved\n")
        
        #check for obj aliases
        print("\tgetting aliases...")
        obj_aliases.update(get_obj_aliases(default_obj_info, obj_names))
        print("\taliases retrieved\n")

        #get objarg info (required and optional args, types, size) 
        print("\tgetting argument info...")
        objarg_info = get_objarg_info(obj_refs, obj_names)
        print("\targument info retrieved\n")
        
        #get attribute info (specific and/or specific attributes, types, size) 
        print("\tgetting attribute info...")
        objattrib_info = get_objattrib_info(obj_refs, obj_names)
        print("\tattribute info retrieved\n")
        
        #get inlet/outlet info (from io files)
        print("\tgetting inlet/outlet info...")
        objinout_info = get_objinout_info(package, obj_names)
        print("\tinlet/outlet info retrieved\n") 
        
        #save maxpy obj info files 
        print("\tsaving object info files...")
        for name in obj_names:
            obj_info = {'default': default_obj_info[name], 
                        'args': objarg_info[name], 
                        'attribs': objattrib_info[name],
                        'in/out': objinout_info[name]}
            
            obj_file = os.path.join(info_folder, name + '.json')
            with open(obj_file, 'w') as f:
                json.dump(obj_info, f, indent=2)
        
        print("\t", len(obj_names), "object info files saved\n")
        print(package, "imported successfully,", len(obj_names), "objects imported\n")
        
    #save aliases
    aliases_file = os.path.join(obj_info_folder, "obj_aliases.json")
    with open(aliases_file, 'w') as f:
        json.dump(obj_aliases, f, indent=2)
    print("object aliases saved successfully")
        
    return


def is_unlisted(ref):
    
    """
    Helper func for saving object info. 
    Returns true if an object is unlisted.
    
    ref --> Max reference file of the object
    """
    
    xmltree = ET.parse(ref)
    root = xmltree.getroot()
    if 'category' in root.attrib.keys():
        category = root.attrib['category']
    else:
        return False
    
    return (category == "Unlisted")


def get_obj_aliases(default_info, names):
    
    """
    Helper for saving obj info. 
    
    Return aliases for objects. 
    """
    
    aliases = {}
    for name in names:
        try:
            default_text = default_info[name]['box']['text']
            if name != default_text: #object name is different from text-field string
                aliases[default_text] = name
        except KeyError:
            pass
    
    return aliases



#************************************************************
#*************** GETTING DEFAULT OBJ INFO *******************
#************************************************************

def get_default_obj_info(package, refs, names):
    """
    Helper function for import_objs().
    Place objects in a MaxPatch and extracts default settings.
    
    *relies on the fact that Max will save 'barebones' objects with default parameters auto-filled in. 
    
    Returns dictionary of {object_name: default_patching_box}
    """
    
    wait_time = get_constant('wait_time')
    
    #create empty patch
    patch = MaxPatch(verbose=False)
    
    #add save+close mechanism to patch 
    add_save_close(patch)
    
    #manually add barebones object dicts to patch
    add_barebones_objs(refs, patch)
    
    #temporarily save patch
    defaultsfile = "defaults_" + package + ".maxpat"
    patch.save(filename=defaultsfile, verbose=False)
    
    #open file, wait for it to save and close
    subprocess.call(['open', defaultsfile])
    time.sleep(wait_time)
    
    #read saved file
    with open(defaultsfile, 'r') as f:
        patchdict = json.loads(f.read())
    
    patchboxes = patchdict['patcher']['boxes'][6:] #ignoring the save/close objects
    
    #parse for object info
    obj_info = {}
    for name, box in zip(names, patchboxes):
        obj_info[name] = box
        
    #remove defaults file
    os.remove(defaultsfile)
        
    return obj_info




def add_barebones_objs(refs, patch):
    """
    Add a barebones instantiation of each object in refs to the patch.
    """
    
    for ref in refs:
        xmltree = ET.parse(ref)
        root = xmltree.getroot()
        text = root.attrib['name'] #get text from xml file
        patch.add_barebones_obj(text)
        
    return 




def add_save_close(patch):
    """
    Helper func for get_default_obj_info.
    Puts thispatcher object arrangement in patch so that it opens, saves, and closes. 
    """
    with open(import_tools, 'r') as f:
        tools = json.loads(f.read())

    patch._patcher_dict['patcher']['boxes'] = tools['boxes']
    patch._patcher_dict['patcher']['lines'] = tools['lines']

    return



#************************************************************
#*************** GETTING OBJ ARGUMENT INFO ******************
#************************************************************

def get_objarg_info(refs, names):
    
    """
    Helper func for import_objs.
    
    Gets info on obj text arguments, returned as dictionary of required and optional arguments. 
    """
    
    #arginfo template
    objarg_info = collections.defaultdict(lambda: {'required':[], 'optional':[]})
    
    #for each obj...
    for ref, name in zip(refs, names):
        
        #parse ref file
        xmltree = ET.parse(ref)
        root = xmltree.getroot()
        
        #get required and optional args
        objarg_info[name]['required'] = get_objargs_by_flag(root, "[@optional='0']")
        objarg_info[name]['optional'] = get_objargs_by_flag(root, "[@optional='1']")
        
    return objarg_info
        

def get_objargs_by_flag(root, flag):
    """
    Retrieves objargs from xml file, according to flag.
    
    Returns a list of cleaned dictionaries, with argument name and type.
    """
    
    findstring = "./objarglist/objarg" + flag
    args = []
    
    for objarg in root.findall(findstring):
        
        #get attrib dict
        objarg = objarg.attrib
        
        #check for placeholder arg
        if not (objarg['name'] == 'OBJARG_NAME' and objarg['type'] == 'OBJARG_TYPE'):
            
            #get argtypes
            if 'type' not in objarg:
                objarg['type'] = []
            else:
                #parse list of possible types, bc reffile might list it as "int, string, or float" etc. 
                objarg['type'] = [type for type in available_argtypes if type in objarg['type']]
            
            #don't need to log the optional flag
            del objarg['optional']
            
            #save to list
            args.append(objarg)
    
    return args
                            

#************************************************************
#*************** GETTING OBJ ATTRIB INFO ********************
#************************************************************
    
    
def get_objattrib_info(refs, names):
    
    """
    Helper func for import_objs.
    
    Gets info on object attributes, returned as a dictionary containing name, type, and size.  
    """
    
    #template for attribute info 
    objattrib_info = collections.defaultdict(lambda: [])
    
    #for each obj...
    for ref, name in zip(refs, names):
        
        #parse xml file
        xmltree = ET.parse(ref)
        root = xmltree.getroot()
        
        #add common box if not UI object
        if 'category' in root.attrib.keys() and root.attrib['category'] != "U/I":
            objattrib_info[name]+= common_box_standin
        
        #get all attributes 
        for attrib in root.findall("./attributelist/attribute"):
            
            attrib_info = attrib.attrib
            
            #remove extraneous info 
            if 'get' in attrib_info.keys():
                del attrib_info['get']
            if 'set' in attrib_info.keys():
                del attrib_info['set']
            
            #save to list
            objattrib_info[name].append(attrib.attrib)

    return objattrib_info
        
                                         
    
#************************************************************
#*************** GETTING OBJ XLET INFO **********************
#************************************************************

    
def get_objinout_info(package, names):
    """
    Helper func for get_default_obj_info.
    
    Returns info about inlets/outlets affected by arguments. 
    *Requires io files for each package, dictating the relationship between arguments and xlets.
    """
    
    objinout_info = {}
    
    #get path to io file
    info_file = os.path.join(obj_io_folder, package + "_io.json")
    
    #read file
    if os.path.exists(info_file):
        with open(info_file, 'r') as f:
            info = json.loads(f.read())
    
    #pull in info
    for name in names:
        if name in info.keys():
            objinout_info[name] = info[name]
        else:
            objinout_info[name] = {}

        
        
    return objinout_info
        


    
    
    

    
    
        