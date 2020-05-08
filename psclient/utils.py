import argparse
import socket
import sys

from tabulate import tabulate

import psclient.config as conf
from psclient.version import *


def parse_options():
    """

    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-H", "--host", default='localhost', help="parstream host")
    parser.add_argument("-p", "--port", default=9011, type=int, help="parstream port")
    parser.add_argument("-u", "--user", help="username")
    parser.add_argument("-t", "--timeout", type=int, help="connection timeout in sec")
    parser.add_argument("-v", "--version", action='store_true', help="enable query timing")

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
    eprint("Type \\ for a list of cli commands\n")


def dump_output(result, time_info=None, timing=False):
    """

    :param result:
    :param time_info:
    :param timing:
    """
    if not result:
        return
    if result.startswith(conf.error_marker):
        print(result)
        return

    if sys.stdout.isatty() and result[0] == '#':
        rows = result[1:].split("\n")
        rows = [r.replace('"', '').split(";") for r in rows]
        print(tabulate(rows, **conf.tabulate_opts))
    else:
        print(result)

    if timing:
        t = time_info['time_info']
        exec_sec = round(t['end_exec'] - t['start'], 4)
        total_sec = round(t['end_out'] - t['start'], 4)

        print()
        print("execution: {} sec".format(exec_sec))
        print("total:     {} sec".format(total_sec))


def safe_execute(client, query):
    """

    :param client:
    :param query:
    :return:
    """
    try:
        return client.execute(query)
    except socket.error as exc:
        print(str(exc), file=sys.stderr)
        print("reconnecting...", file=sys.stderr)

        try:
            client.connect()
            print("successfully connected", file=sys.stderr)
        except ConnectionError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        return None, None
