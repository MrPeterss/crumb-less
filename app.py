import json
import os
import pandas as pd
from flask import Flask
from flask_cors import CORS
from models import db, Business, Review
from routes import register_routes, initialize_data

# Get the directory of the current script
current_directory = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# Configure SQLite database - using 3 slashes for relative path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with app
db.init_app(app)

# Register routes
register_routes(app)

# Function to initialize database and data
def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize database with data from CSV if empty
        if Business.query.count() == 0:
            csv_file_path = os.path.join(current_directory, 'yelp_tucson_food_data_10MB.csv')
            
            print("Loading data from CSV file...")
            df = pd.read_csv(csv_file_path)
            
            # Get unique businesses
            business_cols = ['business_id', 'business_name', 'business_address', 'business_city', 
                           'business_state', 'business_postal_code', 'business_latitude', 
                           'business_longitude', 'business_stars', 'business_review_count', 
                           'business_categories', 'business_hours']
            
            # Create businesses dictionary to avoid duplicates
            businesses_dict = {}
            for _, row in df.iterrows():
                business_id = row['business_id']
                if business_id not in businesses_dict:
                    businesses_dict[business_id] = Business(
                        id=business_id,
                        name=row['business_name'] if pd.notna(row['business_name']) else '',
                        address=row['business_address'] if pd.notna(row['business_address']) else '',
                        city=row['business_city'] if pd.notna(row['business_city']) else '',
                        state=row['business_state'] if pd.notna(row['business_state']) else '',
                        postal_code=str(row['business_postal_code']) if pd.notna(row['business_postal_code']) else '',
                        latitude=float(row['business_latitude']) if pd.notna(row['business_latitude']) else None,
                        longitude=float(row['business_longitude']) if pd.notna(row['business_longitude']) else None,
                        stars=float(row['business_stars']) if pd.notna(row['business_stars']) else None,
                        review_count=int(row['business_review_count']) if pd.notna(row['business_review_count']) else 0,
                        categories=row['business_categories'] if pd.notna(row['business_categories']) else '',
                        hours=row['business_hours'] if pd.notna(row['business_hours']) else ''
                    )
                    db.session.add(businesses_dict[business_id])
            
            print(f"Added {len(businesses_dict)} businesses")
            
            # Add reviews
            review_count = 0
            for _, row in df.iterrows():
                review = Review(
                    id=row['review_id'],
                    user_id=row['user_id'] if pd.notna(row['user_id']) else '',
                    business_id=row['business_id'],
                    stars=float(row['stars']) if pd.notna(row['stars']) else None,
                    date=str(row['date']) if pd.notna(row['date']) else '',
                    text=row['text'] if pd.notna(row['text']) else ''
                )
                db.session.add(review)
                review_count += 1
                
                # Commit in batches to avoid memory issues
                if review_count % 1000 == 0:
                    db.session.commit()
                    print(f"Added {review_count} reviews...")
            
            db.session.commit()
            print(f"Database initialized with {len(businesses_dict)} businesses and {review_count} reviews")
        
        # Initialize data for similarity model (load into plain Python objects)
        initialize_data()
        print("Similarity model initialized")

init_db()

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
