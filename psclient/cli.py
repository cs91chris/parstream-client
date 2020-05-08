import argparse
import os
import sys

from prompt_toolkit import PromptSession, prompt as tkprompt
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.lexers.sql import PlPgsqlLexer
from pygments.styles import get_style_by_name

import psclient.config as conf
import psclient.utils as utils
from psclient import PSClient


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
            utils.eprint("{} missing filename".format(client.error_marker))
            return
        try:
            with open(filename) as f:
                utils.dump_output(*utils.safe_execute(client, f.read()), timing=True)
        except (OSError, RuntimeError) as exc:
            utils.eprint(str(exc))
    elif cmd == "\\d":
        table = args[0] if len(args) > 0 else None
        query = conf.query_tables_list if not table else conf.query_table_info.format(table)

        try:
            utils.dump_output(*utils.safe_execute(client, query))
        except RuntimeError as exc:
            utils.eprint(str(exc))
    elif cmd == "\\q":
        sys.exit(conf.ExitCodes.success)
    else:
        utils.eprint("{} invalid command".format(client.error_marker))


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
        sys.exit(conf.ExitCodes.success)

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
        utils.eprint(str(exc))
        sys.exit(conf.ExitCodes.connection_error)

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
                    utils.dump_output(*utils.safe_execute(client, statement), timing=True)
                except RuntimeError as exc:
                    utils.eprint(str(exc))

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
