error_marker = '#ERROR'

history_file = '.psclient_history'

lexer_style_class = 'vim'

encoding_query = "SELECT VALUE FROM ps_info_configuration WHERE KEY = 'encoding';"

query_tables_list = "SELECT DISTINCT table_name" \
                    " FROM ps_info_column" \
                    " ORDER BY table_name;"

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
    'vacuum', 'values', 'view', 'virtual', 'when', 'where', 'with', 'without'
]

prompt_style = {
    'prompt': '#bfbfbf'
}

tabulate_opts = {
    'headers': 'firstrow',
    'showindex': 'always',
    'tablefmt': 'fancy_grid'
}
