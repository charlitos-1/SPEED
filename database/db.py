import os
import sqlite3
import pandas as pd
import re
import datetime

AMAIAS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
THIS_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(AMAIAS_DIRECTORY, "database", "data.db")

MINER_TABLE_NAME = "miner_queue"
SPEED_DATA_TABLE_NAME = "speed_data"


def generate_timestamp():
    """Generate a timestamp for the request."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def initialize_database(schema, database_path, table_name):
    schema_script = os.path.join(THIS_DIRECTORY, f"{schema}.sql")
    if not os.path.exists(schema_script):
        raise FileNotFoundError(f"Schema file {schema_script} does not exist.")
    execute_sql_script(script=schema_script, db_file=database_path, args={"table_name": table_name})


def sql_string_validator(input_string):
    if not re.match(r"^[a-zA-Z0-9_,\s]*$", input_string):
        raise ValueError("String must only contain letters, numbers, commas, and spaces.")


def get_dummy_df(rows=1, columns=1, header_text="Empty", cell_text="No data"):
    return pd.DataFrame({f"{header_text} {i}": [cell_text]*rows for i in range(columns)})


def get_db_connection(db_file):
    """Returns a connection to the SQLite database."""

    return sqlite3.connect(db_file)


def execute_sql_script(script, db_file, args=None):
    """Executes a SQL script from a file."""

    conn = get_db_connection(db_file)
    cursor = conn.cursor()

    with open(script, "r") as fin:
        sql_script = fin.read()

    if args:
        sql_script = sql_script.format(**args)
    
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()


def table_exists(db_file, table_name):
    """Checks if the specified table exists in the database."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_row(row_data, db_file, table_name):
    """Adds a single row to the specified table."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    columns = ", ".join(row_data.keys())
    placeholders = ", ".join(["?"] * len(row_data))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, tuple(row_data.values()))
    last_row_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return last_row_id
    
    
def delete_row(row_id, db_file, table_name):
    """Deletes a single row from the specified table. WARNING: Don't use this function unless you know what you're doing."""

    sql_string_validator(table_name)
        
    if row_id is None:
        return
    
    if row_id not in get_table_as_df(db_file, table_name)["id"].values:
        return

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    query = f"DELETE FROM {table_name} WHERE id = ?"
    cursor.execute(query, (row_id,))
    conn.commit()
    conn.close()


def add_column(column_name, db_file, table_name):
    """Adds a single column to the specified table."""

    sql_string_validator(table_name)
        
    if column_name in get_column_names(db_file, table_name):
        return
    
    sql_string_validator(column_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    query = f"ALTER TABLE {table_name} ADD COLUMN {column_name}"
    cursor.execute(query)
    conn.commit()
    conn.close()
    
    
def delete_column(column_name, db_file, table_name):
    """Deletes a single column from the specified table. WARNING: Don't use this function unless you know what you're doing."""

    sql_string_validator(table_name)
        
    if column_name not in get_column_names(db_file, table_name):
        return
    
    if is_primary_key(column_name, db_file, table_name):
        return
    
    sql_string_validator(column_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    query = f"ALTER TABLE {table_name} DROP COLUMN {column_name}"
    cursor.execute(query)
    conn.commit()
    conn.close()
    
    
def refactor_columns(columns, db_file, table_name):
    """Refactors the columns of the table. WARNING: Don't use this function unless you know what you're doing."""

    sql_string_validator(table_name)

    for column in columns:
        sql_string_validator(column)
        if column not in get_column_names():
            add_column(column, db_file=db_file, table_name=table_name)
            
    for column in get_column_names():
        sql_string_validator(column)
        if is_primary_key(column, db_file=db_file, table_name=table_name):
            continue
        if column not in columns:
            delete_column(column, db_file=db_file, table_name=table_name)

    return [column.replace(" ", "") for column in columns]


def edit_cell(row_id, column_name, new_value, db_file, table_name):
    """Edits a single cell in the specified table."""

    sql_string_validator(table_name)

    if column_name not in get_column_names(db_file, table_name):
        return
    
    sql_string_validator(column_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    query = f"UPDATE {table_name} SET {column_name} = ? WHERE id = ?"
    cursor.execute(query, (new_value, row_id))
    conn.commit()
    conn.close()
    
    
def edit_row(row_id, new_row_data, db_file, table_name):
    """Edits a single row in the specified table."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    columns = new_row_data.keys()
    query = f"UPDATE {table_name} SET {', '.join([f'{column} = ?' for column in columns])} WHERE id = ?"
    cursor.execute(query, tuple(new_row_data.values()) + (row_id,))
    conn.commit()
    conn.close()
    
    
def get_row(row_id, db_file, table_name):
    """Returns a single row as a dictionary."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name} WHERE id = ?"
    row = pd.read_sql_query(query, conn, params=(row_id,)).to_dict("records")[0]
    conn.close()
    return row


def get_matching_rows(db_file, table_name, args):
    """Returns rows that match the specified arguments as a list of dictionaries."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name} WHERE {' AND '.join([f'{k} = ?' for k in args.keys()])}"
    rows = pd.read_sql_query(query, conn, params=list(args.values())).to_dict("records")
    conn.close()
    return rows


def get_column(column_name, db_file, table_name):
    """Returns a single column as a pandas Series with the id as the index."""

    sql_string_validator(table_name)
        
    if column_name not in get_column_names(db_file, table_name):
        return pd.Series()
    
    sql_string_validator(column_name)

    conn = get_db_connection(db_file)
    query = f"SELECT id, {column_name} FROM {table_name}"
    series = pd.read_sql_query(query, conn, index_col="id")[column_name]
    conn.close()
    return series


def get_table_as_df(db_file, table_name):
    """Returns the specified table as a pandas DataFrame."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_table_as_list(db_file, table_name):
    """Returns the specified table as a list of dictionaries."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name}"
    table = pd.read_sql_query(query, conn).to_dict("records")
    conn.close()
    return table


def is_primary_key(column_name, db_file, table_name):
    """Returns whether the specified column is a primary key."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return column_name == columns[0][1]


def get_column_names(db_file, table_name):
    """Returns the columns of the specified table."""

    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    conn.close()
    return columns


if __name__ == "__main__":
    print(get_column("Input1"))