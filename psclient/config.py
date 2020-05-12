import re
from enum import Enum

error_marker = '#ERROR'
end_response_marker = '\n\n'

json_encoding_regex = re.compile(r"\"value\": \"(.*)\"")
xml_encoding_regex = re.compile(r"<value><!\[CDATA\[(.*)\]\]></value>")

history_file = '.psclient_history'

lexer_style_class = 'vim'

set_format = "SET outputformat = {}"

query_user_list = "SELECT * FROM ps_info_user;"
query_process_info = "SELECT pid, realtime_sec, total_ram_mb FROM ps_info_process;"
query_version = "SELECT parstream_version, build_datetime, source_revision FROM ps_info_version;"
query_configuration_list = "SELECT * FROM ps_info_configuration;"
query_configuration_info = "SELECT * FROM ps_info_configuration WHERE KEY in ({});"

encoding_query = query_configuration_info.format("'encoding'")
format_query = query_configuration_info.format("'outputFormat'")

query_tables_list = "SELECT table_name" \
                    ",import_directory_pattern" \
                    ",import_file_pattern" \
                    ",distribution_column" \
                    ",distribution_redundancy" \
                    " FROM ps_info_table" \
                    " ORDER BY table_name;"

query_cluster_info = "SELECT name,type,host,port,leader,follower,active,online," \
                     "node_status,import_status,merge_status" \
                     " FROM ps_info_cluster_node;"

query_disc_usage_total = "SELECT count(file_name) as files" \
                         ",sum(size_byte) / 1048576 AS MB" \
                         ",sum(size_byte) / 1073741824 AS GB" \
                         ",sum(size_byte) / 1099511627776 AS TB" \
                         " FROM ps_info_disc" \
                         " ORDER BY MB;"

query_disc_usage_partitions = "SELECT path" \
                        ",type" \
                        ",status" \
                        ",sum(size_byte) / 1024 AS KB" \
                        ",sum(size_byte) / 1048576 AS MB" \
                        ",sum(size_byte) / 1073741824 AS GB" \
                        " FROM ps_info_disc" \
                        " WHERE path LIKE '%{}%'" \
                        " GROUP BY path, type, status" \
                        " ORDER BY KB;"

query_partitions_info = "SELECT relative_path AS directory" \
                        ",partition_condition" \
                        ",num_records" \
                        ",status" \
                        " FROM ps_info_partition" \
                        " WHERE table_name = '{}'" \
                        " ORDER BY relative_path;"

query_table_info = "SELECT column_name" \
                    ",sql_type" \
                    ",singularity" \
                    ",has_unique_constraint AS is_unique" \
                    ",has_not_null_constraint AS not_null" \
                    ",is_primary_key" \
                    ",default_value" \
                    " FROM ps_info_column AS c" \
                    " JOIN ps_info_type AS t ON c.value_type_oid = t.oid" \
                    " WHERE table_name = '{}'" \
                   " ORDER BY column_name;"

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
    '\\tables', '\\help', '\\version', '\\settings', '\\timing', '\\pretty',
    '\\file', '\\quit', '\\format', '\\process',
    '\\users', '\\partitions', '\\disc', '\\cluster',

    'tables', 'help', 'version', 'settings', 'timing', 'pretty',
    'file', 'quit', 'format', 'process',
    'users', 'partitions', 'disc', 'cluster',
]

prompt_style = {
    'prompt': 'ansiblue'
}

ps1 = "[{user}{host}:{port}] parstream => "
ps2 = " ... -> "

tabulate_opts = {
    'headers': 'firstrow',
    'tablefmt': 'presto'
}


class ExitCodes(Enum):
    success = 0
    connection_error = 1
