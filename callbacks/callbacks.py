from dash import html, dcc, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import sys

sys.path.append("..")  # Adjust the path to import from the parent directory

from database import db
from layout import layout

def register_callbacks(app):
    @app.callback(
        Output(component_id="database-table", component_property="rowData", allow_duplicate=True),
        Output(component_id="database-table", component_property="columnDefs", allow_duplicate=True),
        Output(component_id="database-store", component_property="data", allow_duplicate=True),
        Input(component_id="database-store", component_property="data"),
        prevent_initial_call="initial_call_duplicate"
    )
    def refresh_database_table(database_store):
        database_store = db.get_table_as_df().to_dict("records")
        row_data = [_ for _ in database_store]
        column_defs = layout.serve_column_defs(db.get_column_names())
        
        return row_data, column_defs, database_store

    @app.callback(
        Output(component_id="dummy-div", component_property="children", allow_duplicate=True),
        Input(component_id="function-1-button", component_property="n_clicks"),
        State(component_id="database-table", component_property="selectedRows"),
        prevent_initial_call=True
    )
    def function_1(n_clicks, selected_rows):
        print("Function 1")
        print(selected_rows)
        
        return no_update

    @app.callback(
        Output(component_id="dummy-div", component_property="children", allow_duplicate=True),
        Input(component_id="function-2-button", component_property="n_clicks"),
        State(component_id="database-table", component_property="selectedRows"),
        prevent_initial_call=True
    )
    def function_2(n_clicks, selected_rows):
        print("Function 2")
        print(selected_rows)
        
        return no_update

    @app.callback(
        Output(component_id="dummy-div", component_property="children", allow_duplicate=True),
        Input(component_id="function-3-button", component_property="n_clicks"),
        State(component_id="database-table", component_property="selectedRows"),
        prevent_initial_call=True
    )
    def function_3(n_clicks, selected_rows):
        print("Function 3")
        print(selected_rows)
        
        return no_update
    
    @app.callback(
        Output(component_id="dummy-div", component_property="children", allow_duplicate=True),
        Input(component_id="function-4-1-button", component_property="n_clicks"),
        State(component_id="database-table", component_property="selectedRows"),
        prevent_initial_call=True
    )
    def function_4_1(n_clicks, selected_rows):
        print("Function 4.1")
        print(selected_rows)
        
        return no_update

    @app.callback(
        Output(component_id="dummy-div", component_property="children", allow_duplicate=True),
        Input(component_id="function-4-2-button", component_property="n_clicks"),
        State(component_id="database-table", component_property="selectedRows"),
        prevent_initial_call=True
    )
    def function_4_2(n_clicks, selected_rows):
        print("Function 4.2")
        print(selected_rows)
        
        return no_update

    @app.callback(
        Output(component_id="dummy-div", component_property="children", allow_duplicate=True),
        Input(component_id="function-4-3-button", component_property="n_clicks"),
        State(component_id="database-table", component_property="selectedRows"),
        prevent_initial_call=True
    )
    def function_4_3(n_clicks, selected_rows):
        print("Function 4.3")
        print(selected_rows)
        
        return no_update


    pass
