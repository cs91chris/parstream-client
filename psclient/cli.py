import argparse
import os
import socket
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.lexers.sql import PlPgsqlLexer
from pygments.styles import get_style_by_name
from tabulate import tabulate
from prompt_toolkit import prompt as tkprompt

import psclient.config as conf
from psclient import PSClient


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
        except ConnectionError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)

        return None, None


def cli_commands(client, cmd, *args):
    """

    :param client:
    :param cmd:
    :param args:
    """
    if cmd == "\\i":
        try:
            filename = args[0]
        except IndexError:
            print("{} missing filename".format(client.error_marker))
            return
        try:
            with open(filename) as f:
                dump_output(*safe_execute(client, f.read()), timing=True)
        except (OSError, RuntimeError) as exc:
            print(str(exc))
    elif cmd == "\\d":
        table = args[0] if len(args) > 0 else None
        query = conf.query_tables_list if not table else conf.query_table_info.format(table)

        try:
            dump_output(*safe_execute(client, query))
        except RuntimeError as exc:
            print(exc)
    elif cmd == "\\q":
        sys.exit(0)
    else:
        print("{} invalid command".format(client.error_marker))


def cli_prompt(session, prompt="> ", is_new=True, is_ignored=False):
    """

    :param session:
    :param prompt:
    :param is_new:
    :param is_ignored:
    :return:
    """
    if sys.stdin.isatty() and not is_new:
        prompt = "-> "
    elif not is_new and is_ignored:
        prompt = ". "

    try:
        if sys.stdout.isatty():
            sys.stdout.flush()
            line = session.prompt(
                prompt,
                auto_suggest=AutoSuggestFromHistory(),
                style=Style.from_dict(conf.prompt_style)
            )
        else:
            sys.stdout.write(prompt)
            sys.stdout.flush()
            line = session.prompt()
    except EOFError:
        sys.exit(0)

    return line


def cli_loop(client, prompt=None):
    """

    :param client:
    :param prompt:
    """
    statement = ""
    lines_ignored = False
    hist_file = os.environ.get('HOME') or '.'

    session = PromptSession(
        history=FileHistory(os.path.join(hist_file, conf.history_file)),
        lexer=PygmentsLexer(PlPgsqlLexer),
        style=style_from_pygments_cls(get_style_by_name(conf.lexer_style_class)),
        completer=WordCompleter(conf.sql_completer)
    )

    if client.username and not client.password:
        client.password = tkprompt('Enter password: ', is_password=True)

    try:
        client.connect()
    except ConnectionError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    while True:
        line = cli_prompt(session, prompt, len(statement) == 0, lines_ignored)
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("--"):
            lines_ignored = True
            continue

        lines_ignored = False

        if sys.stdin.isatty() and line.startswith("\\"):
            cli_commands(client, *line.split())
            continue

        statement = " ".join((statement, line)).lstrip()

        if statement.rstrip().endswith(";"):
            if statement:
                if not sys.stdin.isatty():
                    print()

                try:
                    dump_output(*safe_execute(client, statement), timing=True)
                except RuntimeError as exc:
                    print(str(exc))

            statement = ""


def cli():
    try:
        params = dict()
        params['password'] = None

        parser = argparse.ArgumentParser()
        parser.add_argument("-H", "--host", default='localhost', help="parstream host")
        parser.add_argument("-p", "--port", default=9011, type=int, help="parstream port")
        parser.add_argument("-U", "--user", help="username")
        parser.add_argument("-t", "--timeout", type=int, help="connection timeout in sec")
        args = parser.parse_args()

        params['timeout'] = args.timeout
        params['port'] = args.port
        params['username'] = args.user
        params['host'] = args.host

        cli_loop(
            PSClient(**params), prompt=[(
                "class:prompt", "[{}{}:{}] parstream => ".format(
                    params['username'] + "@" if params['username'] else "",
                    params['host'],
                    params['port']
                )
            )]
        )
    except KeyboardInterrupt:
        print('exited by ctrl+C')
