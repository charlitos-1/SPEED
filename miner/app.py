from flask import Flask, request, jsonify
import os
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import datetime
import sys

AMAIAS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))

DATABASE_PATH = os.path.join(AMAIAS_DIRECTORY, "database", "data.db")
DATABASE_TABLE_NAME = "data"

PROCESSED_DATA_DIR = os.path.join(AMAIAS_DIRECTORY, "processed_data")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

sys.path.append(AMAIAS_DIRECTORY)

from database import db
from data_parser import data_parser

app = Flask("MINER")


@app.route("/process_data", methods=["POST"])
def process_endpoint():
    data = request.get_json()
    raw_data_folder = data.get("raw_data_folder")
    output_folder = data.get("output_folder", PROCESSED_DATA_DIR)

    if not raw_data_folder or not os.path.isdir(raw_data_folder):
        return jsonify({"error": "Invalid or missing raw_data_folder"}), 400
    try:
        data_parser.post_process_data(raw_data_folder, output_folder)
        return jsonify({
            "status": "post_process_requested",
            "output_folder": output_folder
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    app.run(host="0.0.0.0", port=5001, debug=True)


if __name__ == "__main__":
    db.set_default_database_file(DATABASE_PATH)
    db.set_default_database_table_name(DATABASE_TABLE_NAME)
    db.initialize_database()
    app.run(debug=True)
