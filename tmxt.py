"""Transform TMX in a tab-separated text file according to the code list
specified.

Usage:
  tmxt.py --codelist=<langcodes> [--header] [--keep_seg] [--strict] [--multiprops] [INPUT_FILE [OUTPUT_FILE]]

Options:
  --codelist=<langcodes>   Comma-separated list of langcodes (i.e. "en,es").
                           TU propierties can also be specified
  --header                 Print header with column names from --codelist
  --keep_seg               Don't remove 'seg_' prefix from header fields
  --strict                 Don't ignore SIGPIPE
  --multiprops             If there are multiple props with tha same name in a TU or TUV, print JSON array
                           When not enabled, will print the last one only
  
I/O Defaults:
  INPUT_FILE               Defaults to stdin.
  OUTPUT_FILE              Defaults to stdout.
"""

from docopt import docopt
import re
import sys
import json
import xml.parsers.expat

def process_tmx(input, output, codelist, multiprops=False):
    curlang  = ""
    curtuv   = []
    intuv    = False
    inph     = False
    numlangs = 0
    tu       = {}
    intprop  = True
    curtype  = ""
    curprop  = []
    p1       = re.compile(r'\n')
    p2       = re.compile(r'  *')    
    fmt      = ("{}\t"*(len(codelist))).strip()+"\n"
  
    def se(name, attrs):
        nonlocal intuv, intprop, curtuv, curprop, curtype, tu, curlang, codelist, numlangs, inph
        if intuv:
            if name in ["ph", "ept", "bpt", "prop"]:
                inph = True
            curtuv.append("")
        elif name == "tu":
            tu = {i:'' for i in codelist}
        elif name == "tuv":
            if "xml:lang" in attrs:
                curlang = attrs["xml:lang"]
            elif "lang" in attrs:
                curlang = attrs["lang"]
            numlangs += 1
        elif name == "seg":
            curtuv = []
            intuv = True
        elif name == "field":
            pass
        elif name == "prop":
            intprop = True
            curtype = attrs['type']
            if curlang:
                # prepend the lang of the tuv to differentiate between tuv props with the same name
                curtype = f"{curlang}-{curtype}"
            curprop = []
            
    def ee(name):
        nonlocal intuv, intprop, curtuv, curprop, curtype, p1, p2, tu, curlang, codelist, numlangs, fmt, output, inph, multiprops
        if name == "tu":
            # print all collected fields
            # the props are printed as a json array
            tsv_fields = []
            for code in codelist:
                if not isinstance(tu[code], list):
                    tsv_fields.append(tu[code])
                elif multiprops:
                    tsv_fields.append(json.dumps(tu[code]))
                else:
                    if tu[code]:
                        tsv_fields.append(tu[code][0])
                    else:
                        tsv_fields.append("")

            output.write(fmt.format(*tsv_fields))
            numlangs = 0

        elif name == "seg":
            intuv = False
            mystr = p2.sub(' ', p1.sub(' ', "".join(curtuv))).strip()
            tu[curlang] = mystr
            curlang = ""
        elif name == "prop":
            introp = False
            mystr = p2.sub(' ', p1.sub(' ', "".join(curprop))).strip()
            if curtype in tu and isinstance(tu[curtype], list):
                tu[curtype].append(mystr)
            else:
                tu[curtype] = [mystr]
            curtype = ""
        elif name in ["ph", "ept", "bpt", "prop"]:
            inph = False

    def cd(data):
        nonlocal intuv, curtuv, intprop, curprop
        if intuv:
            if not inph:
                curtuv.append(data.replace("\t", " "))
        if intprop:
            curprop.append(data.replace("\t", " "))

    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler  = se
    p.EndElementHandler    = ee
    p.CharacterDataHandler = cd
    p.ParseFile(input) 

def main():
    arguments = docopt(__doc__, version='tmxt 1.1')
    
    input = sys.stdin.buffer if not arguments["INPUT_FILE"] else open(arguments["INPUT_FILE"], "rb")
    output = sys.stdout if not arguments["OUTPUT_FILE"] else open(arguments["OUTPUT_FILE"], "w")    

    codelist_seg = arguments["--codelist"].split(",")
    codelist = [c.replace('seg_', '') for c in codelist_seg]
    header = arguments['--header']
    keep_seg = arguments['--keep_seg']
    strict_mode = arguments['--strict']
    multiprops = arguments['--multiprops']
    
    try:
        if len(codelist) > 0:
            if header:
                if keep_seg:
                    # Don't remove seg_prefix
                    output.write('\t'.join(codelist_seg) + '\n')
                else:
                    output.write('\t'.join(codelist) + '\n')
            process_tmx(input, output, codelist, multiprops)

        input.close()
        output.close()

    except BrokenPipeError as e:
        # Ignore SIGPIPE send by downstream process
        # e.g. head or shuf -n0
        # throw it in strict mode
        if strict_mode:
            raise e

if __name__ == '__main__':
    main()
