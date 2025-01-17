# tmxt

This tool consists on two scripts:
* `tmxplore.py`, a script to determine the language codes available inside a particular TMX file by looking to an excerpt or even the whole file.
* `tmxt.py`, to effectively transform a TMX to a tab-separated text file using the language code list provided in the command. TU propierties can also be printed if requested.

# Requirements

Requires python3 and the libraries included in requirements.txt

## Examples of usage

### `tmxplore.py`

```bash
$ python3 tmxplore.py file.tmx
en es
```

or

```bash
$ cat file.tmx | python3 tmxplore.py
en es
```

### `tmxt.py` 

```bash
$ python3 tmxt.py --codelist en,fr tm.fr-en.tmx en-fr.txt
```

Other

```bash
$ zcat largefile.tmx.gz | python3 tmxt.py --codelist en,es |gzip > bitext.en-es.gz
```

Printing TU propierties
```bash
$ python3 tmxt.py --codelist en,fr,prop1,prop2 tm.fr-en.tmx en-fr.txt
```

For propierties inside the TUV, the language code must be prepended
```bash
$ python3 tmxt.py --codelist en,fr,en-prop1,fr-prop1,prop2 tm.fr-en.tmx en-fr.txt
```

In case a propierty is repeated multiple times inside the same TU or TUV, the last instance will be printed.
To get all of them, add `--multiprops` option and all the propierty instances will be printed in the same TSV field but encoded as a JSON array.
The property can be easily parsed in pythin like
```python
import json
json.loads(fields[3])
```
