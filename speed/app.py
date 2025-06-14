import os
import sys
from dash import Dash

AMAIAS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(AMAIAS_DIRECTORY, "database", "data.db")
DATABASE_TABLE_NAME = "data"

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "assets")

sys.path.append(AMAIAS_DIRECTORY)

from layout import layout
from callbacks import callbacks
from database import db

app = Dash("SPEED", assets_folder=ASSETS_PATH)
app.layout = layout.serve_layout()
callbacks.register_callbacks(app)


def main():
    db.set_default_database_file(DATABASE_PATH)
    db.set_default_database_table_name(DATABASE_TABLE_NAME)
    db.initialize_database()
    app.run(debug=True)


if __name__ == "__main__":
    main()