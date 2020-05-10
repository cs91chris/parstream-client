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


def dump_statement(client, stm, **kwargs):
    """

    :param client:
    :param stm:
    """
    try:
        utils.dump_output(*utils.safe_execute(client, stm), **kwargs)
    except RuntimeError as exc:
        utils.eprint(str(exc))


def cmd_file(client, filename=None):
    """

    :param client:
    :param filename:
    """
    if not filename:
        utils.eprint("{} missing filename".format(client.error_marker))
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
    query = conf.query_tables_list if not table else conf.query_table_info.format(table)
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
        resp, _ = utils.safe_execute(client, conf.set_format.format(fmt))
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


def cmd_partitions(client, table=None):
    """

    :param client:
    :param table:
    """
    if not table:
        utils.eprint("{} table name required".format(client.error_marker))
        return

    dump_statement(client, conf.query_partitions_info.format(table))


def cmd_disc_usage(client, *partitions):
    """

    :param client:
    :param partitions:
    """
    if not partitions:
        query = conf.query_disc_usage_list
    elif partitions[0] == 'total':
        query = conf.query_disc_usage_total
    else:
        partitions = "'{}'".format("','".join(partitions))
        query = conf.query_disc_usage_partitions.format(partitions)

    dump_statement(client, query)


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
    disc=cmd_disc_usage
)
