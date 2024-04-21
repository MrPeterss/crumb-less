import json
import os
from flask import Flask, render_template, request
from flask_cors import CORS
from models.business import Business
from models.review import Review
from models.similarity import Similarity
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

reviews_sql_query = f"""SELECT * FROM reviews"""
reviews_data = mysql_engine.query_selector(reviews_sql_query)
reviews = [Review(row[0], row[1], row[2], row[3], row[4], row[5])
           for row in reviews_data]

businesses_sql_query = f"""SELECT * FROM businesses"""
businesses_data = mysql_engine.query_selector(businesses_sql_query)
businesses = {}
for row in businesses_data:
    businesses[row[0]] = Business(row[0], row[1], row[2], row[3], row[4],
                                  row[5], row[6], row[7], row[8], row[9], row[10], row[11])

sim = Similarity(reviews, businesses)

# Sample search, the LIKE operator in this case is hard-coded,
# but if you decide to use SQLAlchemy ORM framework,
# there's a much better and cleaner way to do this


def sql_search(business):
    query_sql = f"""SELECT * FROM businesses WHERE LOWER( name ) LIKE '%%{business.lower()}%%' limit 10"""

    keys = ['id', 'name', 'address', 'city', 'state', 'postal_code', 'latitude',
            'longitude', 'stars', 'review_count', 'attributes', 'categories', 'hours']
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


def get_businesses_by_id(business_map):
    res = []
    for id, _ in enumerate(business_map):
        if len(res) >= 10:
            break
        res.append(businesses[id])
    return res


def get_business_by_id(name):
    data = None
    if name == "":
        return []
    else:
        business_sql = f"""SELECT id FROM businesses WHERE LOWER( name ) = '{name.lower()}'"""
        data = mysql_engine.query_selector(business_sql)
        if data != None:
            for row in data:
                return row[0]
    return None

# returns businesses matching the cuisine part of the query (maybe we can also
# define a query object so we can keep passing the query into helpers)


def cuisine_diet_search(cuisine, diet):
    data = None
    if cuisine != "NONE" and diet != "NONE":
        business_sql = f"""SELECT DISTINCT id FROM businesses WHERE LOWER( categories ) LIKE '%%{cuisine.lower()}%%' AND LOWER( categories ) LIKE '%%{diet.lower()}%%'"""
        data = mysql_engine.query_selector(business_sql)
    elif cuisine != "NONE":
        business_sql = f"""SELECT DISTINCT id FROM businesses WHERE LOWER( categories ) LIKE '%%{cuisine.lower()}%%'"""
        data = mysql_engine.query_selector(business_sql)
    elif diet != "NONE":
        business_sql = f"""SELECT DISTINCT id FROM businesses WHERE LOWER( categories ) LIKE '%%{diet.lower()}%%'"""
        data = mysql_engine.query_selector(business_sql)
    ids = None
    if data != None:
        ids = []
        for row in data:
            ids.append(row[0])
    return ids


@app.route("/")
def home():
    return render_template('crumbless.html', title="crumbless home")


@app.route("/businesses/search")
def businesses_search():
    text = request.args.get("title")
    return sql_search(text)


@app.route("/reviewsearch")
def review_textmine():
    query = request.args.get("title")
    cuisine = request.args.get("cuisine")
    diet = request.args.get("diet")
    favrestaurant = request.args.get("favrestaurant")
    favrestaurant_id = get_business_by_id(favrestaurant)
    cuisine_ids = cuisine_diet_search(cuisine, diet)
    business_map = sim.text_mining(query, cuisine_ids, favrestaurant_id)
    query_sql = f"""SELECT * FROM businesses WHERE id IN {tuple(list(business_map.keys())[:10])}"""
    keys = ['id', 'name', 'address', 'city', 'state', 'postal_code', 'latitude',
            'longitude', 'stars', 'review_count', 'categories', 'hours']
    data = mysql_engine.query_selector(query_sql)
    return json.dumps([dict(zip(keys, i)) for i in data])


if 'DB_NAME' not in os.environ:
    app.run(debug=True, host="0.0.0.0", port=5001)
