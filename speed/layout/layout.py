from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag


def serve_column_defs(columns):
    column_sizes = {
        "id": {"width": 25, "minWidth": 100, "maxWidth": 500},
        "name": {"width": 100, "minWidth": 100, "maxWidth": 500},
        "date": {"width": 100, "minWidth": 100, "maxWidth": 500},
        "product": {"width": 100, "minWidth": 100, "maxWidth": 500},
        "output_folder": {"width": 100, "minWidth": 100, "maxWidth": 500},
    }
    
    column_defs = [
        {
            "field": column, 
            "headerTooltip": column, 
            "tooltipField": column,
            "headerCheckboxSelection": True if idx == 0 else False,
            "checkboxSelection": True if idx == 0 else False,
            "headerCheckboxSelectionFilteredOnly": True,
            "width": column_sizes.get(column, {}).get("width", "auto"),
            "minWidth": column_sizes.get(column, {}).get("minWidth", 100),
            "maxWidth": column_sizes.get(column, {}).get("maxWidth", 500),
            "filter": True,
            "sortable": False,
        }
        for idx, column in enumerate(columns)
    ]
    return column_defs


def serve_dash_grid_options():
    grid_options = {
        "enableSorting": False,
        "enableColResize": True,
        "animateRows": True,
        "pagination": True,
        "paginationPageSize": 50,
        "paginationPageSizeSelector": True,
        "tooltipShowDelay": 100,
        "rowSelection": "multiple",
        "suppressRowClickSelection": True,
    }
    return grid_options


def serve_layout():
    layout = [
        dbc.Container([
            dbc.Row([
                html.H2("Database"),
            ]),
            dbc.Row([
                dag.AgGrid(id="database-table", rowData=None, columnDefs=serve_column_defs([]), dashGridOptions=serve_dash_grid_options()),
            ]),
            dcc.Store(id="database-store", data=[], storage_type="session"),
            dbc.Row([
                html.Div(id="dummy-div", style={"display":"none"}), # Dummy div to create callbacks with no outputs
                dbc.Button("Function 1", id="function-1-button", color="primary", n_clicks=0),
                dbc.Button("Function 2", id="function-2-button", color="primary", n_clicks=0),
                dbc.Button("Function 3", id="function-3-button", color="primary", n_clicks=0),
                dbc.DropdownMenu(
                    label="Function 4",
                    children=[
                        dbc.DropdownMenuItem("Function 4.1", id="function-4-1-button", n_clicks=0),
                        dbc.DropdownMenuItem("Function 4.2", id="function-4-2-button", n_clicks=0),
                        dbc.DropdownMenuItem("Function 4.3", id="function-4-3-button", n_clicks=0),
                    ],
                ),
            ])
        ]),
    ]
    return layout