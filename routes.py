import json
from flask import render_template, request
from models import db, Business, Review  # SQLAlchemy models
from models.business import Business as BusinessClass  # Plain Python class for similarity
from models.review import Review as ReviewClass  # Plain Python class for similarity
from models.similarity import Similarity

# Global variables - will be initialized in app.py
reviews = None
businesses = None
sim = None

def initialize_data():
    """Initialize reviews, businesses, and similarity model from SQLite database"""
    global reviews, businesses, sim
    
    # Load reviews from database into plain Python objects for similarity model
    review_models = Review.query.all()
    reviews = [ReviewClass(row.id, row.user_id, row.business_id, row.stars, row.date, row.text)
               for row in review_models]

    # Load businesses from database into plain Python objects for similarity model
    business_models = Business.query.all()
    businesses = {}
    for row in business_models:
        businesses[row.id] = BusinessClass(
            row.id, row.name, row.address, row.city, row.state, 
            row.postal_code, row.latitude, row.longitude, row.stars, 
            row.review_count, row.categories, row.hours
        )

    sim = Similarity(reviews, businesses)

def sql_search(business_name):
    """Search for businesses by name using SQLAlchemy"""
    results = Business.query.filter(
        Business.name.ilike(f'%{business_name}%')
    ).limit(10).all()
    
    return json.dumps([{
        'id': b.id,
        'name': b.name,
        'address': b.address,
        'city': b.city,
        'state': b.state,
        'postal_code': b.postal_code,
        'latitude': b.latitude,
        'longitude': b.longitude,
        'stars': b.stars,
        'review_count': b.review_count,
        'categories': b.categories,
        'hours': b.hours
    } for b in results])


def get_business_by_id(name):
    """Get business ID by name"""
    if name == "":
        return None
    
    business = Business.query.filter(Business.name.ilike(name)).first()
    if business:
        return business.id
    return None

def cuisine_diet_search(cuisine, diet):
    """Search for businesses by cuisine and/or diet using SQLAlchemy"""
    query = Business.query
    
    if cuisine != "NONE" and diet != "NONE":
        query = query.filter(
            Business.categories.ilike(f'%{cuisine}%'),
            Business.categories.ilike(f'%{diet}%')
        )
    elif cuisine != "NONE":
        query = query.filter(Business.categories.ilike(f'%{cuisine}%'))
    elif diet != "NONE":
        query = query.filter(Business.categories.ilike(f'%{diet}%'))
    else:
        return None  # Return None when no filter is applied
    
    results = query.distinct().all()
    return [b.id for b in results]

def register_routes(app):
    """Register all routes with the Flask app"""
    
    @app.route("/")
    def home():
        return render_template('crumbless.html', title="crumbless home")

    @app.route("/businesses/search")
    def businesses_search():
        text = request.args.get("title", "")
        return sql_search(text)

    @app.route("/favesearch")
    def fave_search():
        name = request.args.get("fave", "")
        favrestaurant_id = get_business_by_id(name)
        if favrestaurant_id is None or favrestaurant_id == "":
            return json.dumps("")
        else:
            return json.dumps("found")

    @app.route("/name-search")
    def name_search():
        '''Search for a business by name. Returns names of businesses whose name contains the query'''
        name = request.args.get("name", "")
        results = Business.query.filter(
            Business.name.ilike(f'%{name}%')
        ).limit(10).all()
        return json.dumps([b.name for b in results])

    @app.route("/reviewsearch")
    def review_textmine():
        query = request.args.get("title", "")
        cuisine = request.args.get("cuisine", "NONE")
        diet = request.args.get("diet", "NONE")
        favrestaurant = request.args.get("favrestaurant", "")
        
        favrestaurant_id = get_business_by_id(favrestaurant)
        cuisine_ids = cuisine_diet_search(cuisine, diet)
        business_map = sim.text_mining(query, cuisine_ids, favrestaurant_id)
        
        if len(list(business_map.keys())[:10]) == 0:
            return json.dumps("")
        
        # Get top 10 business IDs
        top_business_ids = list(business_map.keys())[:10]
        
        # Query businesses using SQLAlchemy
        results = Business.query.filter(Business.id.in_(top_business_ids)).all()
        
        # Create a mapping for quick lookup
        business_dict = {b.id: b for b in results}
        
        response = {}
        busi_data = []
        
        for business_id in top_business_ids:
            if business_id in business_dict:
                b = business_dict[business_id]
                dict_data = {
                    'id': b.id,
                    'name': b.name,
                    'address': b.address,
                    'city': b.city,
                    'state': b.state,
                    'postal_code': b.postal_code,
                    'latitude': b.latitude,
                    'longitude': b.longitude,
                    'stars': b.stars,
                    'review_count': b.review_count,
                    'categories': b.categories,
                    'hours': b.hours,
                    'similarity': business_map[business_id]
                }
                busi_data.append(dict_data)

        query_dimensions = sim.dimension_scores(query)
        if all(value == 1 for value in query_dimensions.values()):
            query_dimensions = {}    
        response['query_dimensions'] = query_dimensions
        response['sim_score'] = list(business_map.items())[:10]
        response['businesses'] = busi_data

        return json.dumps(response)
