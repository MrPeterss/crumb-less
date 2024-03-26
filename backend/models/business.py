class Business:
    def __init__(self, id, name, address, city, state, postal_code, latitude, longitude, stars, review_count, categories, hours):
        self.id = id
        self.name = name
        self.address = address
        self.city = city
        self.state = state
        self.postal_code = postal_code
        self.latitude = latitude
        self.longitude = longitude
        self.stars = stars
        self.review_count = review_count
        self.categories = categories
        # self.attributes = attributes
        self.hours = hours

    def __repr__(self):
        return f'<Businesses {self.name}>'

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'postal_code': self.postal_code,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'stars': self.stars,
            'review_count': self.review_count,
            'categories': self.categories,
            # 'attributes': self.attributes,
            'hours': self.hours
        }
