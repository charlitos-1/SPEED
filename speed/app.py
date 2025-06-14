import os
import sys
from dash import Dash

from layout import layout
from callbacks import callbacks
from database import db

AMAIAS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')

sys.path.append(AMAIAS_DIRECTORY)

app = Dash("SPEED", assets_folder=ASSETS_PATH)
app.layout = layout.serve_layout()
callbacks.register_callbacks(app)

if __name__ == '__main__':
    db.set_default_database_file("data.db")
    db.set_default_database_table_name("data")
    db.initialize_database()
    app.run(debug=True)