import sys

from prompt_toolkit import HTML, print_formatted_text as fprint
from prompt_toolkit.styles import Style

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


def dump_statement(client, stm, **kwargs):
    """

    :param client:
    :param stm:
    """
    kwargs.setdefault('timing', False)

    try:
        response = client.safe_execute(stm)
        client.dump_output(*response, **kwargs)
    except RuntimeError as exc:
        utils.eprint(str(exc))


def cmd_file(client, filename=None):
    """

    :param client:
    :param filename:
    """
    if not filename:
        utils.eprint("{} missing filename".format(conf.error_marker))
        return

    with open(filename) as f:
        dump_statement(client, f.read(), timing=True)


# noinspection PyUnusedLocal
def cmd_tables(client, table=None, *args):
    """

    :param client:
    :param table:
    :param args:
    """
    if table:
        query = conf.query_table_info.format(table)
    else:
        query = conf.query_tables_list

    dump_statement(client, query)


# noinspection PyUnusedLocal
def cmd_quit(client, *args):
    """

    :param client: not used
    :param args: not used
    """
    sys.exit(conf.ExitCodes.success.value)


# noinspection PyUnusedLocal
def cmd_version(client, *args):
    """

    :param client:
    :param args:
    """
    dump_statement(client, conf.query_version)


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

    dump_statement(client, query)


def cmd_format(client, fmt=None):
    """

    :param client:
    :param fmt:
    """
    if not fmt:
        utils.eprint("missing argument use one of: ASCII, JSON, XML")
        return

    try:
        resp, _ = client.safe_execute(conf.set_format.format(fmt))
        utils.eprint(resp)
    except RuntimeError as exc:
        utils.eprint(str(exc))


# noinspection PyUnusedLocal
def cmd_process(client, *args):
    """

    :param client:
    :param args:
    """
    dump_statement(client, conf.query_process_info)


# noinspection PyUnusedLocal
def cmd_users(client, *args):
    """

    :param client:
    :param args:
    """
    dump_statement(client, conf.query_user_list)


# noinspection PyUnusedLocal
def cmd_cluster(client, *args):
    """

    :param client:
    :param args:
    """
    dump_statement(client, conf.query_cluster_info)


def cmd_partitions(client, table=None):
    """

    :param client:
    :param table:
    """
    if not table:
        utils.eprint("{} table name required".format(conf.error_marker))
        return

    dump_statement(client, conf.query_partitions_info.format(table))


def cmd_disc_usage(client, partition=None):
    """

    :param client:
    :param partition:
    """
    if not partition:
        query = conf.query_disc_usage_total
    else:
        query = conf.query_disc_usage_partitions.format(partition)

    dump_statement(client, query)


# noinspection PyUnusedLocal
def cmd_timing(client, *args):
    """

    :param client:
    """
    t = client.timing
    client.timing = not t

    utils.eprint('timing is: {}'.format('on' if client.timing else 'off'))


# noinspection PyUnusedLocal
def cmd_pretty(client, *args):
    """

    :param client:
    """
    p = client.pretty
    client.pretty = not p

    utils.eprint('pretty is: {}'.format('on' if client.pretty else 'off'))


# noinspection PyUnusedLocal
def cmd_help(client, *args):
    """

    :param client:
    :param args:
    """
    fprint(HTML(
        "The following are the cli commands:"
        "\n\t\\<cmd>help</cmd> - show this message"
        "\n\t\\<cmd>quit</cmd> - exit from client"
        "\n\t\\<cmd>version</cmd> - show parstream's version information"
        "\n\t\\<cmd>timing</cmd> - toggle query timing"
        "\n\t\\<cmd>pretty</cmd> - toggle pretty output"
        "\n\t\\<cmd>users</cmd> - show parstream users"
        "\n\t\\<cmd>process</cmd> - show parstream process information"
        "\n\t\\<cmd>cluster</cmd> - show parstream cluster nodes information"
        "\n\t\\<cmd>tables</cmd> <arg>[table]</arg> - print a table's list or column's list if table given"
        "\n\t\\<cmd>settings</cmd> <arg>[key1 key2]</arg> - prints settings' list of a given keys or all"
        "\n\t\\<cmd>format</cmd> <arg>fmt</arg> - change parstream output format for current session"
        "\n\t\\<cmd>file</cmd> <arg>filename</arg> - executes statements from given file"
        "\n\t\\<cmd>partitions</cmd> <arg>table</arg> - show partitions of given table"
        "\n\t\\<cmd>disc</cmd> <arg>[partition]</arg> - show disk usage or usage of partition LIKE if given"
    ), style=Style.from_dict({
        'cmd': '#ff0066',
        'arg': '#44ff00',
    }))


CLI_COMMANDS = dict(
    tables=cmd_tables,
    version=cmd_version,
    settings=cmd_settings,
    quit=cmd_quit,
    file=cmd_file,
    format=cmd_format,
    process=cmd_process,
    users=cmd_users,
    partitions=cmd_partitions,
    disc=cmd_disc_usage,
    cluster=cmd_cluster,
    pretty=cmd_pretty,
    timing=cmd_timing,
    help=cmd_help
)
