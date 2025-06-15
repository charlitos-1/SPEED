# get absolute path of this file
THIS_DIR=$(dirname "$(readlink -f "$0")")
RAW_DATA_FOLDER=$THIS_DIR

# flask server URL
FLASK_SERVER_URL="http://0.0.0.0:5001"

# endpoint
ENDPOINT="/process_data"

# call curl command
curl -X POST $FLASK_SERVER_URL$ENDPOINT \
    -H "Content-Type: application/json" \
    -d " { \
    \"raw_data_folder\": \"$RAW_DATA_FOLDER\" \
    }"