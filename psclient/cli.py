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
from psclient.commands import command_factory


def cli_prompt(session, prompt="> ", is_new=True):
    """

    :param session:
    :param prompt:
    :param is_new:
    :return:
    """
    if sys.stdin.isatty() and not is_new:
        prompt = conf.ps2

    try:
        if sys.stdout.isatty():
            sys.stdout.flush()
            line = session.prompt(
                prompt,
                auto_suggest=AutoSuggestFromHistory(),
                style=Style.from_dict(conf.prompt_style)
            )
        else:
            line = input()
    except EOFError:
        sys.exit(conf.ExitCodes.success.value)

    return line


def cli_loop(client, prompt=None):
    """

    :param client:
    :param prompt:
    """
    statement = ""
    hist_file = os.environ.get('HOME') or '.'

    if sys.stdout.isatty():
        utils.print_welcome()

        session = PromptSession(
            history=FileHistory(os.path.join(hist_file, conf.history_file)),
            style=style_from_pygments_cls(get_style_by_name(conf.lexer_style_class)),
            completer=WordCompleter(conf.sql_completer + conf.cli_completer),
            lexer=PygmentsLexer(PlPgsqlLexer),
        )
    else:
        session = None

    if client.username and not client.password:
        client.password = tkprompt('Enter password: ', is_password=True)

    try:
        client.connect()
    except ConnectionError as exc:
        utils.eprint(str(exc))
        sys.exit(conf.ExitCodes.connection_error.value)

    while True:
        line = cli_prompt(session, prompt, len(statement) == 0).strip()

        if line and not line.startswith("--"):
            if line.startswith("\\"):
                line = line.split()
                cmd = command_factory(line[0][1:])
                if callable(cmd):
                    cmd(client, *line[1:])
            else:
                statement = " ".join((statement, line)).lstrip()
                if statement.rstrip().endswith(";"):
                    if not sys.stdin.isatty():
                        print()

                    try:
                        resp = utils.safe_execute(client, statement)
                        utils.dump_output(*resp, timing=True)
                    except RuntimeError as exc:
                        utils.eprint(str(exc))

                    statement = ""


def cli():
    try:
        params = dict()
        args = utils.parse_options()

        if args.version:
            utils.dump_version_info()
            sys.exit(conf.ExitCodes.success.value)

        params['host'] = args.host
        params['port'] = args.port
        params['username'] = args.user
        params['password'] = None
        params['timeout'] = args.timeout

        cli_loop(
            PSClient(**params),
            prompt=[(
                "class:prompt", conf.ps1.format(
                    user=params['username'] + "@" if params['username'] else "",
                    host=params['host'],
                    port=params['port']
                )
            )]
        )
    except KeyboardInterrupt:
        print('exited by ctrl+C')
