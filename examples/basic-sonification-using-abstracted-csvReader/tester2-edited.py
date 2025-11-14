import maxpylang as mp

patch = mp.MaxPatch(load_file="tester2.maxpat")

for k, v in patch.objs.items():
    if v._name == "makenote":
        makenote = patch.objs[k]
        break

csv = patch.place("csvReader")[0]
toggle = patch.place("toggle")[0]

patch.connect((csv.outs[0], makenote.ins[1]), 
                (csv.outs[1], makenote.ins[2]),
                (toggle.outs[0], csv.ins[0]))

patch.save("tester2-edited.maxpat")