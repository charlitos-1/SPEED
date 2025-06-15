import os
import sys
import time
import traceback
from datetime import datetime

# Configuration
POLL_INTERVAL = 1
MAX_RETRIES = 3

# Get the parent directory to access other modules
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
AMAIAS_DIRECTORY = os.path.dirname(os.path.dirname(__file__))

sys.path.append(AMAIAS_DIRECTORY)

from database import db
from data_parser import data_parser


def save_processed_data(request, return_data):
    output_folder = request["output_folder"]
    name = return_data.get("name", "?")
    date = return_data.get("date", "?")
    product = return_data.get("product", "?")
    db.add_row(
        {
            "name": name,
            "date": date,
            "product": product,
            "output_folder": output_folder,
        },
        db_file=db.DATABASE_PATH,
        table_name=db.SPEED_DATA_TABLE_NAME
    )

def process_request(request):
    """Process a single request from the queue"""
    row_id = request["id"]
    raw_data_folder = request["raw_data_folder"]
    output_folder = request["output_folder"]
    retry_count = request["retry_count"]

    print(f"[{datetime.now()}] Processing request {row_id}: {raw_data_folder} -> {output_folder}")
    
    try:
        # Update status to PROCESSING
        db.edit_row(
            row_id=row_id, 
            new_row_data={
                "status": "PROCESSING", 
                "updated_at": db.generate_timestamp()
                }, 
            db_file=db.DATABASE_PATH, 
            table_name=db.MINER_TABLE_NAME
        )
        
        # Call the actual processing function
        data_parser_complete, return_data = data_parser.post_process_data(raw_data_folder, output_folder)
        
        if data_parser_complete:
            db.edit_row(
                row_id=row_id, 
                new_row_data={
                    "status": "COMPLETED",
                    "success": 1,
                    "updated_at": db.generate_timestamp()
                }, 
                db_file=db.DATABASE_PATH, 
                table_name=db.MINER_TABLE_NAME
            )
            save_processed_data(request, return_data)
            print(f"[{datetime.now()}] Successfully processed request {row_id}")
        else:
            if retry_count < MAX_RETRIES:
                retry_count += 1
                db.edit_row(
                    row_id=row_id,
                    new_row_data={
                        "status": "QUEUED",
                        "retry_count": retry_count,
                        "updated_at": db.generate_timestamp()
                    },
                    db_file=db.DATABASE_PATH,
                    table_name=db.MINER_TABLE_NAME
                )
                print(f"[{datetime.now()}] Retrying request {row_id} (attempt {retry_count})")
            else:
                error_message = return_data.get("error_message", "Unknown error")
                db.edit_row(
                    row_id=row_id, 
                    new_row_data={
                        "status": "FAILED",
                        "error_message": error_message,
                        "retry_count": MAX_RETRIES,
                        "updated_at": db.generate_timestamp()
                    }, 
                    db_file=db.DATABASE_PATH,
                    table_name=db.MINER_TABLE_NAME
                )
                print(f"[{datetime.now()}] Failed request {row_id} after {MAX_RETRIES} attempts")
        return True
        
    except Exception as e:
        error_message = str(e)
        print(f"[{datetime.now()}] Error processing request {row_id}: {error_message}")
        print(traceback.format_exc())
        
        # Update with error status
        db.update_request_status(row_id, "ERROR", error_message, db_file=db.DATABASE_PATH)
        return False
    

def get_queued_requests(limit):
    """Retrieve queued requests from the database"""
    queued_requests = db.get_matching_rows(
        db_file=db.DATABASE_PATH,
        table_name=db.MINER_TABLE_NAME,
        args={
            "status": "QUEUED"
        }
    )

    queued_requests.sort(key=lambda x: x["created_at"])

    return queued_requests[:limit] if queued_requests else []


def worker_loop():
    """Main worker loop that polls for queued requests"""
    print(f"[{datetime.now()}] Starting worker process")
    db.initialize_database(schema=db.MINER_TABLE_NAME, database_path=db.DATABASE_PATH, table_name=db.MINER_TABLE_NAME)
    db.initialize_database(schema=db.SPEED_DATA_TABLE_NAME, database_path=db.DATABASE_PATH, table_name=db.SPEED_DATA_TABLE_NAME)
    
    while True:
        try:
            # Get queued requests (limit to processing one at a time for simplicity)
            queued_requests = get_queued_requests(limit=1)
            
            if not queued_requests:
                time.sleep(POLL_INTERVAL)
                continue
                
            request = queued_requests[0]
            process_request(request)
                
        except Exception as e:
            print(f"[{datetime.now()}] Worker error: {e}")
            print(traceback.format_exc())
            time.sleep(POLL_INTERVAL)  # Wait before trying again


if __name__ == "__main__":
    worker_loop()
