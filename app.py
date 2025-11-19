import json
import os
from flask import Flask
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler
from routes import register_routes, initialize_data

# ROOT_PATH for linking with all your files.
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
LOCAL_MYSQL_USER = "root"
LOCAL_MYSQL_USER_PASSWORD = ""
LOCAL_MYSQL_PORT = 3306
LOCAL_MYSQL_DATABASE = "crumblessdb"

app = Flask(__name__)
CORS(app)

# Register routes
register_routes(app)

# Function to initialize database and data
def init_db():
    with app.app_context():
        # Initialize MySQL connection
        mysql_engine = MySQLDatabaseHandler(
            LOCAL_MYSQL_USER, LOCAL_MYSQL_USER_PASSWORD, LOCAL_MYSQL_PORT, LOCAL_MYSQL_DATABASE)
        
        # Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
        mysql_engine.load_file_into_db()
        
        # Initialize data (reviews, businesses, similarity model)
        initialize_data(mysql_engine)
        print("Database and data initialized")

init_db()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
