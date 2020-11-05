import os
import sys

import click
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
from psclient import CLIClient
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
            sys.stdout.flush()
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
            lexer=PygmentsLexer(PlPgsqlLexer)
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
                        client.dump_output(*client.safe_execute(statement))
                    except RuntimeError as exc:
                        utils.eprint(str(exc))

                    statement = ""


@click.command()
@click.option("-H", "--host", default='localhost', help="parstream host")
@click.option("-p", "--port", default=9011, type=int, help="parstream port")
@click.option("-P", "--password", default=None, type=int, help="password")
@click.option("-u", "--username", default=None, help="username")
@click.option("-t", "--timeout", default=None, type=int, help="connection timeout in sec")
@click.option("-v", "--version", is_flag=True, flag_value=True, default=False, help="show client version info")
@click.option("--no-timing", is_flag=True, flag_value=True, default=False, help="disable query timing")
@click.option("--no-pretty", is_flag=True, flag_value=True, default=False, help="disable pretty output")
def cli(host, port, username, password, timeout, version, no_timing, no_pretty):
    """

    :param host:
    :param port:
    :param username:
    :param password:
    :param timeout:
    :param version:
    :param no_timing:
    :param no_pretty:
    """
    try:
        if version:
            utils.dump_version_info()
            sys.exit(conf.ExitCodes.success.value)

        client = CLIClient(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            timing=not no_timing,
            pretty=not no_pretty
        )

        cli_loop(
            client,
            prompt=[("class:prompt", conf.ps1.format(
                user=username + "@" if username else "",
                host=host,
                port=port
            ))]
        )
    except KeyboardInterrupt:
        print('exited by ctrl+C')
