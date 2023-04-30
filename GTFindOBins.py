from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

import csv
import json
import click
import magic
import os
import requests


def display_banner() -> None:
    """Displays a banner with the name of the script and some additional information."""
    ascii_banner = '''
  ________________         ______  ___  _        
 / ___/_  __/ __(_)__  ___/ / __ \/ _ )(_)__  ___
/ (_ / / / / _// / _ \/ _  / /_/ / _  / / _ \(_-<
\___/ /_/ /_/ /_/_//_/\_,_/\____/____/_/_//_/___/
                                                 
    '''
    click.echo(ascii_banner)
    click.echo('# Probably Useless Script Coded By Marcin Chryczyk (@nWwWm)')
    click.echo('# By the way, I didn\'t expect anyone to use this option ;)')
    click.echo('________________________________________________________')
    click.echo()


def display_output(data: list[tuple[str, str]], all: bool = False) -> None:
    for line in data:
        if line[1] is None and all:
            click.echo(f'[-] {line[0]} --> NOT FOUND (verbose mode)')
        elif line[1]:
            click.echo(f'[+] {line[0]} --> {line[1]}')


def read_file(filename: str) -> list[str]:
    """Reads the data from the file.

    Args:
        filename: Filename string. File supported formats: json, txt, csv

    Returns:
        List with strings.
    """
    mime = magic.from_file(filename, mime=True)
    ext = filename.split('.')[-1]
    data = []

    if ext not in ['json', 'txt', 'csv']:
        raise NotImplementedError('File extension not supported.')

    with open(filename, 'r') as f:
        # check extension for csv file first because mime is the same as txt file.
        if mime == 'text/plain' and ext == 'csv':
            reader = csv.reader(f)
            data = list(reader)[0]
        elif mime == 'text/plain':
            # Strip new line character
            data = [line.strip() for line in f.readlines()]
        elif mime == 'application/json' and ext == 'json':
            data = json.load(f)
    return data


def is_anchor_on_site(url: str, anchor: str) -> bool:
    """Checks if the anchor is on the page."""

    try:
        result = requests.get(url, timeout=10)
        result.raise_for_status()
    except (requests.exceptions.HTTPError, requests.exceptions.Timeout):
        return False

    try:
        doc = BeautifulSoup(result.text, 'html.parser')
    except:
        return False

    return doc.find('a', {'href': anchor}) is not None


def get_gtfobins_link(binary_name: str, function_name: str | None = None) -> tuple[str, str | None]:
    """Scrapes the GTFOBins website for the provided binary and function, and prints out the corresponding link."""

    url = f'https://gtfobins.github.io/gtfobins/{binary_name}/'
    result = requests.get(url)

    if result.status_code == 404:
        return (binary_name, None)

    doc = BeautifulSoup(result.text, 'html.parser')

    if function_name is None:
        # if function name is not given, return link to the binary page
        return (binary_name, url)
    else:
        # if function name is given, search for that function in the page
        # On the site, anchor names are lowercase function names and instead of spaces they are -
        function_anchor = function_name.lower().replace(' ', '-')

        if is_anchor_on_site(url, f'/gtfobins/{binary_name}/#{function_anchor}'):
            return (f'{binary_name}+{function_name}', url + f'#{function_anchor}')
        else:
            return (f'{binary_name}+{function_name}', None)


def gtfobins_scrapper(binary_name: list[str], function_name: list[str] | None = None) -> None:
    """Scrapes the GTFOBins website for links to binaries, or binaries with functions."""
    data = []
    features = []

    with ThreadPoolExecutor() as e:
        if function_name:
            for bin in binary_name:
                for func in function_name:
                    features.append(e.submit(get_gtfobins_link, bin, func))
        else:
            for bin in binary_name:
                features.append(e.submit(get_gtfobins_link, bin, None))

    for feature in features:
        data.append(feature.result())

    return data


@click.command()
@click.argument('binary')
@click.option('-f', '--function', help='Name, filename or list (e.g. Sudo,SUID) of functions.')
@click.option('--banner/--no-banner', '-B/ ', default=False, help='Display script banner.')
@click.option('-v/ ', '--verbose/--no-verbose', default=False)
def cli(binary: str, function: str, banner: bool, verbose: bool) -> None:
    """GTFinderOBins is a script that searches the GTFOBins website for pages related to a given list of binaries and functions.

    BINARY is the name, filename or list (e.g. nmap,base32) of binaries.

    Supported file types: json | txt | csv
    """

    if banner:
        display_banner()

    if os.path.isfile(binary):
        try:
            binaries = read_file(binary)
        except NotImplementedError:
            click.echo(
                'Error: Oops! That was not a valid file extension. For more info --help')
            return
    else:
        binaries = binary.split(',')

    try:
        if os.path.isfile(function):
            functions = read_file(function)
        else:
            functions = function.split(',')
    except TypeError:
        functions = None
    except NotImplementedError:
        click.echo(
            'Error: Oops! That was not a valid file extension. For more info --help')
        return

    data = gtfobins_scrapper(binaries, functions)
    display_output(data, verbose)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
