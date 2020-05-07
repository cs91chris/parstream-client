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
