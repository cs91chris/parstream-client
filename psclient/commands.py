import sys

import psclient.config as conf
import psclient.utils as utils


def command_factory(cmd):
    """

    :param cmd:
    :return:
    """
    try:
        return CLI_COMMANDS[cmd]
    except KeyError:
        utils.eprint("invalid command '{}'".format(cmd))


def cmd_file(client, filename=None):
    """

    :param client:
    :param filename:
    """
    if not filename:
        utils.eprint("{} missing filename".format(client.error_marker))
        return

    try:
        with open(filename) as f:
            utils.dump_output(*utils.safe_execute(client, f.read()), timing=True)
    except (OSError, RuntimeError) as exc:
        utils.eprint(str(exc))


# noinspection PyUnusedLocal
def cmd_tables(client, table=None, *args):
    """

    :param client:
    :param table:
    :param args:
    """
    query = conf.query_tables_list if not table else conf.query_table_info.format(table)
    try:
        utils.dump_output(*utils.safe_execute(client, query))
    except RuntimeError as exc:
        utils.eprint(str(exc))


# noinspection PyUnusedLocal
def cmd_quit(client, *args):
    """

    :param client: not used
    :param args: not used
    """
    sys.exit(conf.ExitCodes.success.value)


# noinspection PyUnusedLocal
def cmd_version(client, *args):
    try:
        utils.dump_output(*utils.safe_execute(client, conf.query_version))
    except RuntimeError as exc:
        utils.eprint(str(exc))


def cmd_settings(client, *args):
    """

    :param client:
    :param args:
    """
    if not args:
        query = conf.query_configuration_list
    else:
        settings = "'{}'".format("','".join(args))
        query = conf.query_configuration_info.format(settings)
    try:
        utils.dump_output(*utils.safe_execute(client, query))
    except RuntimeError as exc:
        utils.eprint(str(exc))


def cmd_format(client, fmt=None):
    """

    :param client:
    :param fmt:
    """
    if not fmt:
        utils.eprint("missing argument use one of: ASCII, JSON, XML")
        return

    try:
        resp, _ = utils.safe_execute(client, conf.set_format.format(fmt))
        utils.eprint(resp)
    except RuntimeError as exc:
        utils.eprint(str(exc))


CLI_COMMANDS = dict(
    tables=cmd_tables,
    version=cmd_version,
    settings=cmd_settings,
    quit=cmd_quit,
    file=cmd_file,
    format=cmd_format
)
