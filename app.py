from dash import Dash
from layout.layout import serve_layout
from callbacks.callbacks import register_callbacks
from database.db import initialize_database, set_default_database_file, set_default_database_table_name

app = Dash(__name__)

app.layout = serve_layout()

register_callbacks(app)

if __name__ == '__main__':
    set_default_database_file("data.db")
    set_default_database_table_name("data")
    initialize_database()
    app.run(debug=True)