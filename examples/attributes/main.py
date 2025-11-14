import maxpylang as mp

patch = mp.MaxPatch()
bar = patch.place("playbar")[0]
g = patch.place("jit.movie @moviefile crashtest.mov")[0]
window = patch.place("jit.pwindow")[0]
patch.connect([bar.outs[0], g.ins[0]])
patch.connect([g.outs[0], window.ins[0]])
patch.save("attributes.maxpat")