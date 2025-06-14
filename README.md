# SPEED

This project is a Dash application designed to display metadata of test runs for a manufacturing site. It utilizes a SQLite database to store metadata and a Redis cache for improved performance. The application allows users to select a test run and visualize the corresponding data stored in Parquet files.

## Project Structure

```
dash-manufacturing-app
├── app.py                # Main entry point of the Dash application
├── assets
│   └── css
│       └── custom.css    # Custom CSS for styling the Dash app
├── callbacks             # Directory containing callback functions
│   └── callbacks.py      # Callback functions for user interactions
├── layout                # Directory containing layout definitions
│   └── layout.py         # Layout components of the Dash app
├── database              # Directory for database management
│   ├── db.py             # SQLite database connection and queries
│   └── schema.sql        # SQL schema for creating database tables
├── cache                 # Directory for caching mechanisms
│   └── redis_cache.py     # Redis cache setup and operations
├── requirements.txt      # Project dependencies
└── README.md             # Documentation for the project
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd SPEED
   ```

2. **Create a Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up the Database**
   - Run the SQL schema to create the necessary tables in the SQLite database.
   - Ensure that the database file is created and accessible.

5. **Run the Application**
   ```bash
   python app.py
   ```

6. **Access the App**
   Open your web browser and navigate to `http://127.0.0.1:8050` to view the application.

## Usage Guidelines

- The main page displays a table of metadata for test runs.
- Select a test run from the table to visualize the corresponding data.
- The application retrieves data from the SQLite database and uses Redis for caching to enhance performance.

## Future Enhancements

- Consider deploying the application on Azure for broader accessibility.
- Implement additional features based on user feedback and requirements.