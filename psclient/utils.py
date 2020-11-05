import json
import sys

import click
import pygments
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import PygmentsTokens
from pygments.lexers.data import JsonLexer
from pygments.lexers.html import HtmlLexer
from tabulate import tabulate

import psclient.config as conf
from psclient.version import *


def pretty_print(data, arg=None):
    """

    :param data:
    :param arg:
    """
    lexer = None

    if arg == 'JSON':
        data = json.dumps(json.loads(data), indent=2)
        lexer = JsonLexer()
    elif arg == 'XML':
        lexer = HtmlLexer()
    elif arg == 'ASCII':
        if not data.startswith(conf.error_marker):
            rows = data[1:].split("\n")
            rows = [r.replace('"', '').split(";") for r in rows if r]
            data = tabulate(rows, **conf.tabulate_opts)
            return click.echo_via_pager(data)
        else:
            return eprint(data)

    if lexer:
        tokens = list(pygments.lex(data, lexer=lexer))
        print_formatted_text(PygmentsTokens(tokens))
    else:
        print(data)


def dump_version_info():
    """

    """
    print("version:", __version__)
    print("author:", __author__)
    print("license:", __license__)
    print("url:", __url__)


def eprint(message=None, colored=True):
    """

    :param message:
    :param colored:
    """
    colored = colored and sys.stdin.isatty()
    if colored:
        click.secho(message, err=True, fg="red")
    else:
        print(message, file=sys.stderr)


def print_welcome():
    """

    """
    eprint("Unofficial Cisco Parstream cli")
    eprint("Type \\help for a list of cli commands\n")
