import socket
import sys

from tabulate import tabulate

import psclient.config as conf


def eprint(*args):
    """

    :param args:
    """
    print(*args, file=sys.stderr)


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
