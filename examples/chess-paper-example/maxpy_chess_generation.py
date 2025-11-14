import maxpylang as mp 
import sys


row_coords = [8, 7, 6, 5, 4, 3, 2, 1]
column_coords = ["a", "b", "c", "d", "e", "f", "g", "h"]
piece_map = {
    "R": "rook",
    "N": "knight",
    "B": "bishop",
    "K": "king",
    "Q": "queen",
    "P": "pawn"
}


def get_synth_info(char, row_ind, col_ind):
    """
    Put all synth info into a list. 
    """
    if char.isupper():
        color = "white"
    else:
        color = "black"
    
    piecename = piece_map[char.upper()]
    info = [piecename, color, row_ind, col_ind]

    return info



def build_patch(synth_info, board_ind): 
    """
    Build and save a MaxMSP patch from a list of synth info.
    """
    #create empty patch 
    patch = mp.MaxPatch()
    
    
    #create ezdac
    patch.set_position(500, 900)
    ezdac = patch.place("ezdac~")[0]
    
    #make all synth objects 
    for synth in synth_info:
        
        #get info
        piecename = synth[0]
        color = synth[1]
        row_ind = synth[2]
        col_ind = synth[3] 
        
        #make objects w/ specified size 
        synth = mp.MaxObject(     piecename + "-synth"                 , patching_rect = [0, 0, 100, 22])
        color_msg = mp.MaxObject( "message " + color                   , patching_rect = [0, 0, 40, 20])
        col_msg = mp.MaxObject(   "message " + column_coords[col_ind]  , patching_rect = [0, 0, 20, 20])
        row_msg = mp.MaxObject(   "message " + str(row_coords[row_ind]), patching_rect = [0, 0, 20, 20])
        
        #place objects at custom placements 
        patch.place(synth, color_msg, col_msg, row_msg, 
                    spacing_type = "custom",
                    spacing = [ (col_ind*120 + 100, row_ind*100 + 100),
                                (col_ind*120 + 100, row_ind*100 + 100 - 25),
                                (col_ind*120 + 150, row_ind*100 + 100 - 25),
                                (col_ind*120 + 180, row_ind*100 + 100 - 25) ])
        
        #connect objects 
        patch.connect( (color_msg.outs[0], synth.ins[0]),
                       (col_msg.outs[0]  , synth.ins[1]),
                       (row_msg.outs[0]  , synth.ins[2]),
                       (synth.outs[0]    , ezdac.ins[0]) )
        
    #save patch 
    patch.save("generated-boards/" + str(board_ind))
    
    
    
def main() -> int:
    
    #first, read file with FEN strings into a list of split FEN strings  
    fen_strings = []
    with open("fens.txt", "r") as fenfile:
        lines = fenfile.read().splitlines()
        for line in lines: 
            split_line = line.split("/")
            fen_strings.append(split_line)

    #then, process all FEN strings
    for board_ind in range(len(fen_strings)):

        synth_info = [] #save info for synths to make

        #process each row
        for row_ind in range(8):
            row = fen_strings[board_ind][row_ind]

            col_ind = 0 #track column coordinate 
            #for each char in each row
            for char in row:  
                if char.isnumeric():
                    col_ind += int(char) #handle numbers in strings
                else:
                    info = get_synth_info(char, row_ind, col_ind)
                    synth_info.append(info)
                    col_ind += 1

        #build patch from synth info 
        build_patch(synth_info, board_ind)
        
    return 0
    
    
if __name__ == '__main__':
    sys.exit(main())  
