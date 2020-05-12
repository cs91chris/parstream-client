import argparse
import json
import sys

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
            rows = [r.replace('"', '').split(";") for r in rows]
            data = tabulate(rows, **conf.tabulate_opts)

    if lexer:
        tokens = list(pygments.lex(data, lexer=lexer))
        print_formatted_text(PygmentsTokens(tokens))
    else:
        print(data)


def parse_options():
    """

    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-H", "--host", default='localhost', help="parstream host")
    parser.add_argument("-p", "--port", default=9011, type=int, help="parstream port")
    parser.add_argument("-u", "--user", help="username")
    parser.add_argument("-t", "--timeout", type=int, help="connection timeout in sec")
    parser.add_argument("-v", "--version", action='store_true', help="show client version info")
    parser.add_argument("--no-timing", action='store_false', help="disable query timing")
    parser.add_argument("--no-pretty", action='store_false', help="disable pretty output")

    return parser.parse_args()


def dump_version_info():
    """

    """
    print("version:", __version__)
    print("author:", __author__)
    print("license:", __license__)
    print("url:", __url__)


def eprint(*args):
    """

    :param args:
    """
    print(*args, file=sys.stderr)


def print_welcome():
    """

    """
    eprint("Unofficial Cisco Parstream cli")
    eprint("Type \\help for a list of cli commands\n")
