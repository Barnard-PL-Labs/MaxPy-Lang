import maxpylang as mp

patch = mp.MaxPatch(load_file="mcfm.maxpat")

#create a smaller dictionary, only holding "random"
# objects that will be replaced with "stocksounds" abstraction patch
Selective_Random_Limit = 10
replace = {}
for k, v in patch.objs.items():
    if v._name == "random" and int(v._args[0])>Selective_Random_Limit:
        replace[k] = v

#loop through dict of all "random objects" and replace with abstraction patch
for k, v in replace.items():

    patch.replace(k, "stocksounds", True, True)

patch.save("stockSonification.maxpat")