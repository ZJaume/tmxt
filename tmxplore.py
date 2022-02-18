"""Explore TMX files to get all different language codes.

Usage:
  tmxplore.py [options] [INPUT_FILE]

Options:
  --no_tus=<n>  Explore the first n translation units at much [default: 10].
  --all         Explore all the file.
  --props       Explore props type.
  --delimiter=<d>
                Delimiter to the output codelist [default:  ]
  
I/O Defaults:
  INPUT_FILE        Defaults to stdin.
"""

from docopt import docopt
import xml.parsers.expat
import sys

def print_result(langlist, delimiter=' '):
    print(delimiter.join(langlist))
    sys.exit(0)

def explore(fd, ntus=10, props=False):
    langset  = set()
    langlist = []
    proplist = []
    ntu = 0

    def se(name, attrs):
        nonlocal ntu
        if name == "tuv":
            if "xml:lang" in attrs:
                lang = attrs["xml:lang"].lower()
            elif "lang" in attrs:
                lang = attrs["lang"].lower()

            if props:
                lang = 'seg_' + lang

            if lang not in langset:
                langlist.append(lang)
                langset.add(lang)

        elif name == "tu":
            ntu += 1
            if ntu >= ntus + 1:
                return langlist + proplist

        elif props and name == "prop":
            if attrs["type"] not in proplist:
                proplist.append(attrs["type"])

    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = se
    p.ParseFile(fd)

    return langlist + proplist

def main():
    arguments = docopt(__doc__, version='tmxplore 1.0')

    fd = sys.stdin.buffer if not arguments["INPUT_FILE"] else open(arguments["INPUT_FILE"], "rb")
    if arguments["--all"]:
        codelist = explore(fd, sys.maxsize, arguments["--props"])
    else:
        codelist = explore(fd, int(arguments["--no_tus"]), arguments["--props"])
    print_result(codelist, arguments["--delimiter"])

    fd.close()

if __name__ == '__main__':
    main()

