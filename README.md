# GTFindOBins

GTFindOBins.py is a Python script that searches the [GTFOBins](https://github.com/GTFOBins/GTFOBins.github.io) [website](https://gtfobins.github.io/) for pages related to a given list of programs. It is intended to be used as a command-line tool and takes a list of program names as an argument, along with an optional function name. When it finds a suitable page, it returns a link to it.

## Installation

To use GTFinderOBins, you must have Python 3.10 or above installed on your system. You can download Python 3 from the official website: https://www.python.org/downloads/

Once you have Python 3 installed, you can install the required dependencies using pip:

```console
foo@bar:~$ pip install -r requirements.txt
```

## Usage

To use GTFinderOBins, run the script with the following arguments:
```console
foo@bar:~$ python GTFindOBins.py BINARY -f [function]
```

* `[BINARY]`: the name, filename or list (e.g. Sudo,SUID (NO SPACES)) of binaries to search for.
* `[function]` the name, filename or list (e.g. Sudo,SUID (NO SPACES)) of a functions to search for on the GTFObins website.

For more syntax inforamtions run:
```console
foo@bar:~$ python GTFindOBins.py --help
```

For example:
```console
foo@bar:~$ python GTFindOBins.py binaries.txt -f SUID
```

This command would search the GTFObins website for pages related to the programs listed in programs.txt, and return links to pages that include the SUID function.

## Contributing

If you find a bug or have a suggestion for how to improve GTFinderOBins, please open an issue on the GitHub repository. If you would like to contribute code, please submit a pull request with your changes.

## License

GTFinderOBins is released under the Open Source License. See LICENSE for more information.
