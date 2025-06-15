from flask import Flask, request, jsonify
import os
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import datetime
import sys

AMAIAS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))

PROCESSED_DATA_DIR = os.path.join(AMAIAS_DIRECTORY, "processed_data")
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

sys.path.append(AMAIAS_DIRECTORY)

from database import db

app = Flask("MINER")


def add_to_queue(raw_data_folder, output_folder):
    """Add a new request to the processing queue."""
    row_data = {
        "raw_data_folder": raw_data_folder,
        "output_folder": output_folder,
        "status": "QUEUED",
        "created_at": db.generate_timestamp(),
        "updated_at": db.generate_timestamp()
    }
    request_id = db.add_row(row_data, db_file=db.DATABASE_PATH, table_name=db.MINER_TABLE_NAME)
    request_data = db.get_row(request_id, db_file=db.DATABASE_PATH, table_name=db.MINER_TABLE_NAME)
    return request_data


@app.route("/process_data", methods=["POST"])
def process_endpoint():
    data = request.get_json()
    raw_data_folder = data.get("raw_data_folder")
    output_folder = data.get("output_folder", PROCESSED_DATA_DIR)

    if not raw_data_folder or not os.path.isdir(raw_data_folder):
        return jsonify({"error": "Invalid or missing raw_data_folder"}), 400
    try:
        request_data = add_to_queue(raw_data_folder, output_folder)
        return jsonify(request_data), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    db.initialize_database(schema=db.MINER_TABLE_NAME, database_path=db.DATABASE_PATH, table_name=db.MINER_TABLE_NAME)
    app.run(host="0.0.0.0", port=5001, debug=True)

if __name__ == "__main__":
    main()
