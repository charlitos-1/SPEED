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

SPEED_DATA_TABLE_NAME = "speed_data"

app = Dash("SPEED", assets_folder=ASSETS_PATH)
app.layout = layout.serve_layout()
callbacks.register_callbacks(app)


def main():
    db.initialize_database(schema=SPEED_DATA_TABLE_NAME, database_path=db.DATABASE_PATH, table_name=SPEED_DATA_TABLE_NAME)
    app.run(host="0.0.0.0", port=5050, debug=True)


if __name__ == "__main__":
    main()