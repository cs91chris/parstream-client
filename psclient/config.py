from enum import Enum

error_marker = '#ERROR'

history_file = '.psclient_history'

lexer_style_class = 'vim'

set_format = "SET outputformat = {}"
query_user_list = "SELECT * FROM ps_info_user;"
query_process_info = "SELECT pid, realtime_sec, total_ram_mb FROM ps_info_process;"
query_version = "SELECT parstream_version, build_datetime, source_revision FROM ps_info_version;"
query_configuration_list = "SELECT * FROM ps_info_configuration;"
query_configuration_info = "SELECT * FROM ps_info_configuration WHERE KEY in ({});"
encoding_query = "SELECT VALUE FROM ps_info_configuration WHERE KEY = 'encoding';"
query_tables_list = "SELECT DISTINCT table_name FROM ps_info_column ORDER BY table_name;"
query_disc_usage_total = "SELECT count(file_name) as files" \
                         ",((sum(size_byte) / 1000) / 1000) / 1000 AS GB" \
                         ",(((sum(size_byte) / 1000) / 1000) / 1000) / 10000 AS TB" \
                         "FROM ps_info_disc;"
query_disc_usage_list = "SELECT path" \
                        ",type" \
                        ",status" \
                        ",(sum(size_byte) / 1000) / 1000 AS MB" \
                        ",((sum(size_byte) / 1000) / 1000) / 1000 AS GB" \
                        "FROM ps_info_disc" \
                        "GROUP BY path, type, status;"
query_disc_usage_partitions = "SELECT path" \
                        ",type" \
                        ",status" \
                        ",(sum(size_byte) / 1000) / 1000 AS MB" \
                        ",((sum(size_byte) / 1000) / 1000) / 1000 AS GB" \
                        "FROM ps_info_disc" \
                        "WHERE path IN ({})" \
                        "GROUP BY path, type, status;"
query_partitions_info = "SELECT table_name" \
                        ",base_directory || relative_path AS directory" \
                        ",partition_condition" \
                        ",num_records" \
                        ",status" \
                        ",access_time" \
                        "FROM ps_info_partition" \
                        "WHERE table_name = '{}';"
query_table_info = "SELECT column_name" \
                    ",column_type" \
                    ",type_name" \
                    ",value_singularity" \
                    " FROM ps_info_column AS c" \
                    " JOIN ps_info_type AS t ON c.value_type_oid = t.oid" \
                    " WHERE table_name = '{}';"

sql_completer = [
    'abort', 'action', 'add', 'after', 'all', 'alter', 'analyze', 'and',
    'as', 'asc', 'attach', 'autoincrement', 'before', 'begin', 'between',
    'by', 'cascade', 'case', 'cast', 'check', 'collate', 'column',
    'commit', 'conflict', 'constraint', 'create', 'cross', 'current_date',
    'current_time', 'current_timestamp', 'database', 'default',
    'deferrable', 'deferred', 'delete', 'desc', 'detach', 'distinct',
    'drop', 'each', 'else', 'end', 'escape', 'except', 'exclusive',
    'exists', 'explain', 'fail', 'for', 'foreign', 'from', 'full', 'glob',
    'group', 'having', 'if', 'ignore', 'immediate', 'in', 'index',
    'indexed', 'initially', 'inner', 'insert', 'instead', 'intersect',
    'into', 'is', 'isnull', 'join', 'key', 'left', 'like', 'limit',
    'match', 'natural', 'no', 'not', 'notnull', 'now' 'null', 'of', 'offset',
    'on', 'or', 'order', 'outer', 'plan', 'pragma', 'primary', 'query',
    'raise', 'recursive', 'references', 'regexp', 'reindex', 'release',
    'rename', 'replace', 'restrict', 'right', 'rollback', 'row',
    'savepoint', 'select', 'set', 'table', 'temp', 'temporary', 'then',
    'to', 'transaction', 'trigger', 'union', 'unique', 'update', 'using',
    'vacuum', 'values', 'view', 'virtual', 'when', 'where', 'with', 'without',
]

cli_completer = [
    '\\tables', '\\help', '\\version', '\\settings',
    '\\file', '\\quit', '\\format', '\\process',
    '\\users', '\\partitions', '\\disc'
]

prompt_style = {
    'prompt': 'ansiblue'
}

ps1 = "[{user}{host}:{port}] parstream => "
ps2 = " ... -> "

tabulate_opts = {
    'headers': 'firstrow',
    'showindex': 'always',
    'tablefmt': 'fancy_grid'
}


class ExitCodes(Enum):
    success = 0
    connection_error = 1
