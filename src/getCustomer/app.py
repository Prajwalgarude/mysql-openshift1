import os
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Initialize CORS for the Flask app.
# This allows cross-origin requests, which is essential for front-end applications
# hosted on a different domain/port to interact with this API.
CORS(app)

# Database connection details retrieved from environment variables.
# This is a secure way to handle sensitive information, keeping it out of the codebase.
USER = os.getenv('MYSQL_USER')
PASSWORD = os.environ.get('MYSQL_PASSWORD')
HOST = os.environ.get('MYSQL_HOST')
DATABASE = os.getenv('MYSQL_DATABASE')

def get_db_connection():
    """
    Establishes and returns a new MySQL database connection.
    This function is called for each request to ensure a fresh and active connection,
    which is a more robust approach than a single global connection, especially in
    multi-threaded environments.
    """
    try:
        conn = mysql.connector.connect(
            host=str(HOST),
            user=str(USER),
            passwd=str(PASSWORD),
            db=str(DATABASE)
        )
        print("Database connection established for request.")
        return conn
    except Exception as e:
        print(f"ERROR: Could not connect to Database: {e}")
        # Re-raise the exception to be caught by the route's error handling
        raise

@app.route('/')
def home():
    """
    Home route for the API.
    Returns a simple welcome message.
    """
    # Using jsonify for consistent API response format, even for simple messages.
    return jsonify({'message': 'Welcome to getCustomerList version 1.1'})

@app.route('/customers', methods=['GET'])
def getCustomerList():
    """
    Retrieves a list of customers (id, customerName) from the database.
    The results are ordered by customerName and then by id.
    Returns:
        JSON: A list of customer dictionaries or an error message.
    """
    conn = None # Initialize connection to None
    cursor = None # Initialize cursor to None
    try:
        conn = get_db_connection() # Get a new connection for this request
        cursor = conn.cursor()

        sql = "SELECT id, customerName FROM customer ORDER BY customerName, id"
        cursor.execute(sql)

        # Get column names from the cursor description to create dictionary keys
        columns = [column[0] for column in cursor.description]
        myresult = cursor.fetchall()

        json_data = []
        for result in myresult:
            # Combine column names with fetched data to create a list of dictionaries
            json_data.append(dict(zip(columns, result)))

        print(f"Retrieved customer data: {json_data}")
        # Return the data as a JSON response with a 200 OK status
        return jsonify(json_data), 200

    except mysql.connector.Error as err:
        # Catch specific database errors for more precise handling
        print(f"Database error: {err}")
        return jsonify({'error': f"Database query failed: {err}"}), 500
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f"An internal server error occurred: {e}"}), 500
    finally:
        # Ensure the cursor and connection are closed, regardless of success or failure
        if cursor:
            cursor.close()
            print("Cursor closed.")
        if conn and conn.is_connected():
            conn.close()
            print("Database connection closed.")

# This block ensures that the Flask development server runs only when the script
# is executed directly (e.g., `python app.py`), not when imported as a module.
if __name__ == '__main__':
    # Run the Flask application on all available network interfaces (0.0.0.0)
    # and on port 8080. debug=True enables debug mode, which provides
    # a debugger and auto-reloader, useful during development.
    app.run(host="0.0.0.0", port=8080, debug=True)
