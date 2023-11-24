#import json5
import json
import sys
from tree import *

# This is partially done import from the i3's layouts.
# a. Existing layouts can be read by read_objs. This ignores all the comments.
# b. New layouts can be preprocessed by this hack:
#         i3-save-tree  | (read _; sed -e 's#// split.*$##' -e 's#^\( *\)//#\1  #') | jq . --slurp
#
# Missing parts:
# 1. JSON to Toplevel
# 2. Toplevel to Python, maybe using ats.unparse (and indent it using tokenize)
#
# Optionally, we could also recognize known patterns in the regexes and generate the rest.
#


def read_obj(f, parse):
    # Reads a JSON object from stream
    # Utterly slow (quadratic complexity), expecially with json5 library.
    # Unclean code (Pokémon exception handling).
    # But somehow works.
    # PoC quality (PoC = Piece of Crap)
    
    buff = b''
    while True:
        r = f.readline()    # readline is usually OK, and it makes the code much faster than reading just one byte or one char.
        buff += r
        if len(r) == 0:
            if len(buff.strip()) == 0:
                raise EOFError()
            json5.loads(buff)
            raise Exception("failed to fail")
        #print(buff)
        try:
            return parse(buff)
        except Exception as e:
            #print(e)
            pass


def read_objs(f, parse):
    objs = []
    while True:
        try:
            objs.append(read_obj(f, parse))
        except EOFError:
            return objs


#data = read_objs(sys.stdin.buffer, json5.loads) #json5.load(sys.stdin)
#print(json.dumps(data))
