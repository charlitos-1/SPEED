import os
import sqlite3
import pandas as pd
import re

default_database_file:str = None
default_database_table_name:str = None

SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")

def set_default_database_file(file_path):
    global default_database_file
    default_database_file = file_path


def set_default_database_table_name(table_name):
    global default_database_table_name
    default_database_table_name = table_name


def sql_string_validator(input_string):
    if not re.match(r"^[a-zA-Z0-9_,\s]*$", input_string):
        raise ValueError("String must only contain letters, numbers, commas, and spaces.")


def get_dummy_df(rows=1, columns=1, header_text="Empty", cell_text="No data"):
    return pd.DataFrame({f"{header_text} {i}": [cell_text]*rows for i in range(columns)})


def get_db_connection(db_file=None):
    """Returns a connection to the SQLite database."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    return sqlite3.connect(db_file)


def initialize_database(db_file=None, table_name=None):
    """ call database schema creation function to initialize the database and table """
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file
    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
    if table_exists(db_file, table_name):
        return
    execute_sql_script(SCHEMA_FILE, {"table_name": table_name}, db_file=db_file)


def execute_sql_script(script, args=None, db_file=None):
    """Executes a SQL script from a file."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    conn = get_db_connection(db_file)
    cursor = conn.cursor()

    with open(script, "r") as fin:
        sql_script = fin.read()

    if args:
        sql_script = sql_script.format(**args)
    
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()


def table_exists(db_file=None, table_name=None):
    """Checks if the specified table exists in the database."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_row(row_data, db_file=None, table_name=None):
    """Adds a single row to the specified table."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    columns = ", ".join(row_data.keys())
    placeholders = ", ".join(["?"] * len(row_data))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, tuple(row_data.values()))
    conn.commit()
    conn.close()
    
    
def delete_row(row_id, db_file=None, table_name=None):
    """Deletes a single row from the specified table. WARNING: Don't use this function unless you know what you're doing."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
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


def add_column(column_name, db_file=None, table_name=None):
    """Adds a single column to the specified table."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
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
    
    
def delete_column(column_name, db_file=None, table_name=None):
    """Deletes a single column from the specified table. WARNING: Don't use this function unless you know what you're doing."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
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
    
    
def refactor_columns(columns, db_file=None, table_name=None):
    """Refactors the columns of the table. WARNING: Don't use this function unless you know what you're doing."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name

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


def edit_cell(row_id, column_name, new_value, db_file=None, table_name=None):
    """Edits a single cell in the specified table."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
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
    
    
def edit_row(row_id, new_row_data, db_file=None, table_name=None):
    """Edits a single row in the specified table."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    columns = new_row_data.keys()
    query = f"UPDATE {table_name} SET {', '.join([f'{column} = ?' for column in columns])} WHERE id = ?"
    cursor.execute(query, tuple(new_row_data.values()) + (row_id,))
    conn.commit()
    conn.close()
    
    
def get_row(row_id, db_file=None, table_name=None):
    """Returns a single row as a dictionary."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name} WHERE id = ?"
    row = pd.read_sql_query(query, conn, params=(row_id,)).to_dict("records")[0]
    conn.close()
    return row


def get_column(column_name, db_file=None, table_name=None):
    """Returns a single column as a pandas Series with the id as the index."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)
        
    if column_name not in get_column_names(db_file, table_name):
        return pd.Series()
    
    sql_string_validator(column_name)

    conn = get_db_connection(db_file)
    query = f"SELECT id, {column_name} FROM {table_name}"
    series = pd.read_sql_query(query, conn, index_col="id")[column_name]
    conn.close()
    return series


def get_table_as_df(db_file=None, table_name=None):
    """Returns the specified table as a pandas DataFrame."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_table_as_list(db_file=None, table_name=None):
    """Returns the specified table as a list of dictionaries."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    query = f"SELECT * FROM {table_name}"
    table = pd.read_sql_query(query, conn).to_dict("records")
    conn.close()
    return table


def is_primary_key(column_name, db_file=None, table_name=None):
    """Returns whether the specified column is a primary key."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    conn.close()
    return column_name == columns[0][1]


def get_column_names(db_file=None, table_name=None):
    """Returns the columns of the specified table."""
    if db_file is None:
        if default_database_file is None:
            raise ValueError("Database file is not set.")
        db_file = default_database_file

    if table_name is None:
        if default_database_table_name is None:
            raise ValueError("Database table name is not set.")
        table_name = default_database_table_name
        
    sql_string_validator(table_name)

    conn = get_db_connection(db_file)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [column[1] for column in cursor.fetchall()]
    conn.close()
    return columns


if __name__ == "__main__":
    print(get_column("Input1"))