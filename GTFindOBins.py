from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

import csv
import json
import click
import magic
import os
import pkg_resources
import pyfiglet
import requests


def get_version() -> str:
    try:
        return pkg_resources.require('gtfinderobins')[0].version
    except:
        return '-'

def banner() -> None:
    """Displays a banner with the name of the script and some additional information."""
    ascii_banner = pyfiglet.figlet_format('GTFindOBins', font='smkeyboard')
    click.echo(ascii_banner)
    click.echo('# Probably Useless Script Coded By Marcin Chryczyk (@nWwWm)')
    click.echo('# version: ' + get_version())
    click.echo('________________________________________________________')
    click.echo()


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
    with open(filename, 'r') as f:
            # check extension for csv file first because mime is the same as txt file.
            if ext == 'csv':
                reader = csv.reader(f)
                data = list(reader)[0]
            elif mime == 'text/plain' and ext == 'txt':
                # Strip new line character
                data = [line.strip() for line in f.readlines()]
            elif mime == 'application/json' and ext == 'json':
                data = json.load(f)
            else:
                raise NotImplementedError('File extension support not implemented.')
    return data


def is_anchor_on_site(url: str, anchor: str) -> bool:
    """Checks if the anchor is on the page."""
    result = requests.get(url)
    if result.status_code != 200:
        return False
    doc = BeautifulSoup(result.text, 'html.parser')
    return doc.find('a', {'href': anchor}) is not None


def get_gtfobins_link(binary_name: str, function_name: str = None) -> None:
    """Scrapes the GTFOBins website for the provided binary and function, and prints out the corresponding link.

    Args:
        binary_name: The name of the binary to search for on the GTFOBins website.
        function_name: The name of the function to search for on the binary's page. Defaults to None.

    Returns:
        None: The function does not return anything, but prints out the link to the binary or function if found.

    """
    if binary_name is None:
        click.echo('No binaries provided')
        return None

    url = f'https://gtfobins.github.io/gtfobins/{binary_name}/'
    result = requests.get(url)

    if result.status_code == 404:
        click.echo(f"No link found for binary: {binary_name}")
        return None

    doc = BeautifulSoup(result.text, 'html.parser')
    
    if function_name is None:
        # if function name is not given, return link to the binary page
        click.echo(url)
    else:
        # if function name is given, search for that function in the page
        if is_anchor_on_site(url, f'/gtfobins/{binary_name}/#{function_name}'):
            click.echo(url + f'#{function_name}')
             
        else:
           click.echo(f"No Link found for function: {function_name} in binary: {binary_name}")
        
    
def gtfobins_scrapper(bins: list[str] | None, funcs: list[str] | None) -> None:
    """Scrapes the GTFOBins website for links to binaries or functions, or both.
    
    Args:
        bins: A list of binary names to search for.
        funcs: A list of function names to search for.

    Returns:
        None: The function does not return any values.
    
    """
    data = []
    if bins is not None and funcs is not None:
        # Both parameters provided
        with ThreadPoolExecutor() as e:
            for bin in bins:
                for func in funcs:
                    e.submit(get_gtfobins_link, bin, func)
    elif bins is not None:
        # Only bins parameter provided
        with ThreadPoolExecutor() as e:
            for bin in bins:
                e.submit(get_gtfobins_link, bin)
    elif funcs is not None:
        # Only func parameter provided
        get_gtfobins_link(None, funcs)
    else:
        # No parameters provided
        pass

@click.command()
@click.option('-b', '--binary', help='Binary name or file name with binaries')
@click.option('-f', '--function', help='Function name or file name with functions')   
def cli(binary: str, function: str) -> None:
    """GTFinderOBins is a script that searches the GTFOBins website for pages related to a given list of binaries and functions."""
    
    try:
        if os.path.isfile(binary):
            binaries = read_file(binary)
        else:
            binaries = binary.split(',')
    except TypeError:
        binaries = None

    try:    
        if os.path.isfile(function):
            functions = read_file(function)
        else:
            functions = function.split(',')
    except TypeError:
        functions = None
    
    gtfobins_scrapper(binaries, functions)


def main() -> None:
    banner()
    cli()

if __name__ == "__main__":
    main()