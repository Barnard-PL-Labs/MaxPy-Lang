import maxpylang as mp 

patch = mp.MaxPatch()

#Objects (titled abbreviation of object name)
numNotes = 10
togglePosition = numNotes*80 + 100
tg = patch.place("toggle", num_objs=numNotes, starting_pos=[0, 100])
gt = patch.place("gate", num_objs=numNotes, starting_pos=[0,200])
btn = patch.place("button", num_objs=numNotes, starting_pos=[0,300])

rnd = patch.place("random 120", num_objs=1, starting_pos=[0,400])[0]
num = patch.place("number", num_objs=1, starting_pos=[0,500])[0]
mn = patch.place("makenote 100 100 2", num_objs=1, starting_pos=[0,600])[0]
no = patch.place("noteout int 1", num_objs=1, starting_pos=[0,700])[0]

tg2 = patch.place("toggle", num_objs=1, starting_pos=[togglePosition, 100])[0]
mtr = patch.place("metro 100", num_objs=1, starting_pos=[togglePosition, 150])[0]
cnt = patch.place("counter " + str(numNotes) + " 1", num_objs=1, starting_pos=[togglePosition, 200])[0]
num2 = patch.place("number", num_objs=1, starting_pos=[togglePosition, 250])[0]

#creating a sel object to filter as many counter signals as specified by value of numNotes
selHelper = "sel "
for i in range(1, numNotes+1):
    selHelper += str(i)
    selHelper += " "
sel = patch.place(selHelper, num_objs=1, starting_pos=[togglePosition, 300])[0]

#Connecting objects
for t, g in zip(tg, gt):
    patch.connect([t.outs[0], g.ins[0]])

for g, b in zip(gt, btn):
    patch.connect([g.outs[0], b.ins[0]])

for g, b in zip(gt, btn):
    patch.connect([g.outs[0], b.ins[0]])

for b in btn:
    patch.connect([b.outs[0], rnd.ins[0]])

patch.connect([rnd.outs[0], num.ins[0]])
patch.connect([num.outs[0], mn.ins[0]])
patch.connect([mn.outs[0], no.ins[0]])
patch.connect([mn.outs[1], no.ins[1]])

patch.connect([tg2.outs[0], mtr.ins[0]])
patch.connect([mtr.outs[0], cnt.ins[0]])
patch.connect([cnt.outs[0], num2.ins[0]])
patch.connect([num2.outs[0], sel.ins[0]])

i=0
for g in gt:
    patch.connect([sel.outs[i], g.ins[1]])
    i+=1

patch.save("tester2.maxpat")