import os
import mysql.connector
from flask import Flask, request, render_template, jsonify # Added jsonify for better JSON responses
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Database connection details from environment variables
USER = os.getenv('MYSQL_USER')
PASSWORD = os.environ.get('MYSQL_PASSWORD')
HOST = os.environ.get('MYSQL_HOST')
DATABASE = os.getenv('MYSQL_DATABASE')

# Initialize database connection globally
# It's generally better to manage connections per request or use a connection pool
# but for a simple script, this global approach is common.
mydb = None
mycursor = None

try:
    mydb = mysql.connector.connect(
        host=str(HOST),
        user=str(USER),
        passwd=str(PASSWORD),
        db=str(DATABASE)
    )
    mycursor = mydb.cursor()
    print("Database successfully connected")

except Exception as e:
    print("Could not connect to Database")
    print(f"Error: {e}") # Use f-strings for better error message formatting

@app.route('/')
def home():
    """
    Home route for the API.
    """
    return 'getCustomer version 1.1'

@app.route('/customer/<id>')
def getCustomer(id):
    """
    Retrieves customer details by ID from the database.
    Args:
        id (str): The ID of the customer to retrieve.
    Returns:
        JSON: Customer data or an error message.
    """
    # Ensure the database connection is active
    if not mydb or not mydb.is_connected():
        try:
            global mydb, mycursor # Re-establish connection if lost
            mydb = mysql.connector.connect(
                host=str(HOST),
                user=str(USER),
                passwd=str(PASSWORD),
                db=str(DATABASE)
            )
            mycursor = mydb.cursor()
            print("Re-established database connection")
        except Exception as e:
            return jsonify({"error": f"Database connection failed: {e}"}), 500

    sql = "SELECT * FROM customer WHERE id = %s" # Use %s for parameter substitution
    try:
        # Pass parameters as a tuple or dictionary, %s is generally safer for positional args
        mycursor.execute(sql, (str(id),)) 
        
        columns = [column[0] for column in mycursor.description] # Get column names directly
        myresult = mycursor.fetchall()
        
        json_data = []
        for result in myresult:
            json_data.append(dict(zip(columns, result)))

        print(json_data)
        
        if json_data:
            # jsonify automatically handles serialization and sets Content-Type header
            return jsonify(json_data[0]) 
        else:
            # Return a 404 Not Found status if no customer is found
            return jsonify({"message": f"No customer found with ID: {id}"}), 404
            
    except Exception as e:
        # Return a 500 Internal Server Error for database retrieval issues
        return jsonify({"error": f"Could not retrieve records from DB: {e}"}), 500

# This ensures the Flask app runs only when the script is executed directly
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
