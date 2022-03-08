"""Transform TMX in a tab-separated text file according to the code list
specified.

Usage:
  tmxt.py --codelist=<langcodes> [--header] [--keep_seg] [INPUT_FILE [OUTPUT_FILE]]

Options:
  --codelist=<langcodes>   Comma-separated list of langcodes (i.e. "en,es").
                           TU propierties can also be specified
  --header                 Print header with column names from --codelist
  --keep_seg               Don't remove 'seg_' prefix from header fields
  
I/O Defaults:
  INPUT_FILE               Defaults to stdin.
  OUTPUT_FILE              Defaults to stdout.
"""

from docopt import docopt
import re
import sys
import xml.parsers.expat

def process_tmx(input, output, codelist):
    curlang  = ""
    curtuv   = []
    intuv    = False
    numlangs = 0
    tu       = {}
    intprop  = True
    curtype  = ""
    curprop  = []
    p1       = re.compile(r'\n')
    p2       = re.compile(r'  *')    
    fmt      = ("{}\t"*(len(codelist))).strip()+"\n"

    def se(name, attrs):
        nonlocal intuv, intprop, curtuv, curprop, curtype, tu, curlang, codelist, numlangs
        if intuv:
            curtuv.append("")
        elif name == "tu":
            tu = {i:'' for i in codelist}
        elif name == "tuv":
            if "xml:lang" in attrs:
                curlang = attrs["xml:lang"].lower()
            elif "lang" in attrs:
                curlang = attrs["lang"].lower()
            numlangs += 1
        elif name == "seg":
            curtuv = []
            intuv = True
        elif name == "prop":
            intprop = True
            curtype = attrs['type']
            curprop = []
            
    def ee(name):
        nonlocal intuv, intprop, curtuv, curprop, curtype, p1, p2, tu, curlang, codelist, numlangs, fmt, output
        if name == "tu":
            output.write(fmt.format(*[tu[code] if not isinstance(tu[code], list) else '\t'.join(tu[code][:numlangs]) for code in codelist]))
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

    def cd(data):
        nonlocal intuv, curtuv, intprop, curprop
        if intuv:
            curtuv.append(data)
        if intprop:
            curprop.append(data)

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
    
    if len(codelist) > 1:
        if header:
            if keep_seg:
                # Don't remove seg_prefix
                output.write('\t'.join(codelist_seg) + '\n')
            else:
                output.write('\t'.join(codelist) + '\n')
        process_tmx(input, output, codelist)
    
    input.close()
    output.close()

if __name__ == '__main__':
    main()

