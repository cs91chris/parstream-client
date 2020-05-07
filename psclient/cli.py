import getopt
import getpass
import os
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

import psclient.config as conf
from psclient import PSClient


def dump_output(result, time_info=None, timing=False):
    """

    :param result:
    :param time_info:
    :param timing:
    """
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
        time_info = time_info['time_info']
        exec_sec = round(time_info['end_exec'] - time_info['start'], 3)
        total_sec = round(time_info['end_out'] - time_info['start'], 3)

        print()
        print("execution: {} sec".format(exec_sec))
        print("total:     {} sec".format(total_sec))


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
                dump_output(*client.execute(f.read()), timing=True)
        except (OSError, RuntimeError) as exc:
            print(str(exc))
    elif cmd == "\\d":
        table = args[0] if len(args) > 0 else None
        query = conf.query_tables_list if not table else conf.query_table_info.format(table)

        try:
            dump_output(*client.execute(query))
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


def cli_password():
    try:
        return getpass.getpass().replace("'", "''")
    except EOFError:
        sys.exit(0)


def cli_parse_args():
    """

    :return:
    """
    def print_usage():
        print(
            "Usage: "
            "[-H | --host= <host>] "
            "[-p | --port= <port>] "
            "[-U | --username= <username>] "
        )

    params = dict()
    params['username'] = None
    params['password'] = None
    params['port'] = 9042
    params['host'] = "localhost"
    params['timeout'] = 60

    try:
        opts, _ = getopt.getopt(
            sys.argv[1:], 'hH:p:U:',
            ["help", "host=", "port=", "username="]
        )
    except getopt.GetoptError:
        print_usage()
        sys.exit(1)

    for o, a in opts:
        if o in ("-H", "--host"):
            params['host'] = a
        elif o in ("-p", "--port"):
            params['port'] = int(a)
        elif o in ("-U", "--username"):
            params['username'] = a
        elif o in ("-h", "--help"):
            print_usage()
            sys.exit(0)
        else:
            print_usage()
            sys.exit(1)

    return params


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

    client.connect()

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
            if statement.lstrip().lower().startswith("login"):
                parts = statement.split()
                if len(parts) == 2:
                    client.password = cli_password()
                    statement = statement.rstrip("; ")
                    statement += ' ' + client.password

            statement = statement.rstrip("; ")
            if statement:
                if not sys.stdin.isatty():
                    print()

                try:
                    dump_output(*client.execute(statement), timing=True)
                except RuntimeError as exc:
                    print(str(exc))

            statement = ""


def cli():
    try:
        kwargs = cli_parse_args()
        if kwargs['username']:
            kwargs['password'] = cli_password()

        cli_loop(
            PSClient(**kwargs), prompt=[(
                "class:prompt", "[{}{}:{}] parstream => ".format(
                    kwargs['username'] + "@" if kwargs['username'] else "",
                    kwargs['host'],
                    kwargs['port']
                )
            )]
        )
    except KeyboardInterrupt:
        print('exited by ctrl+C')
