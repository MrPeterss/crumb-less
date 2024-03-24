import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from helpers.MySQLDatabaseHandler import MySQLDatabaseHandler

# ROOT_PATH for linking with all your files.
# Feel free to use a config.py or settings.py with a global export variable
os.environ['ROOT_PATH'] = os.path.abspath(os.path.join("..", os.curdir))

# These are the DB credentials for your OWN MySQL
# Don't worry about the deployment credentials, those are fixed
# You can use a different DB name if you want to
LOCAL_MYSQL_USER = "root"
LOCAL_MYSQL_USER_PASSWORD = ""
LOCAL_MYSQL_PORT = 3306
LOCAL_MYSQL_DATABASE = "crumblessdb"

mysql_engine = MySQLDatabaseHandler(
    LOCAL_MYSQL_USER, LOCAL_MYSQL_USER_PASSWORD, LOCAL_MYSQL_PORT, LOCAL_MYSQL_DATABASE)

# Path to init.sql file. This file can be replaced with your own file for testing on localhost, but do NOT move the init.sql file
mysql_engine.load_file_into_db()

app = Flask(__name__)
CORS(app)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this


def sql_search(business):
    query_sql = f"""SELECT * FROM businesses WHERE LOWER( name ) LIKE '%%{business.lower()}%%' limit 10"""

    keys = ['id', 'name', 'address', 'city', 'state', 'postal_code', 'latitude',
            'longitude', 'stars', 'review_count', 'attributes', 'categories', 'hours']
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


def tok_categories(categories):
    # returns a set of tokens
    return

# returns businesses matching the cuisine part of the query (maybe we can also
# define a query object so we can keep passing the query into helpers)


def cuisine_search(cuisine):
    query_sql = f"""SELECT * FROM businesses WHERE LOWER( categories ) LIKE '%%{cuisine.lower()}%%'"""
    keys = ['id', 'name', 'address', 'city', 'state', 'postal_code', 'latitude',
            'longitude', 'stars', 'review_count', 'attributes', 'categories', 'hours']
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


def jaccard_sim(cat1, cat2):
    tok_attr1 = tok_categories(cat1)
    tok_attr2 = tok_categories(cat2)
    return len(tok_attr1.intersection(tok_attr2)) / len(tok_attr1.union(tok_attr2))


@app.route("/")
def home():
    return render_template('crumbless.html', title="crumbless home")


@app.route("/businesses/search")
def businesses_search():
    text = request.args.get("title")
    return sql_search(text)


if 'DB_NAME' not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5000)
