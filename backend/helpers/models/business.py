class Businesses:
  def __init__(self, id, name, categories, stars, review_count, address, city, state, postal_code, latitude, longitude, attributes, hours):
    self.id = id
    self.name = name
    self.categories = categories
    self.stars = stars
    self.review_count = review_count
    self.address = address
    self.city = city
    self.state = state
    self.postal_code = postal_code
    self.latitude = latitude
    self.longitude = longitude
    self.attributes = attributes
    self.hours = hours

  def __repr__(self):
    return f'<Businesses {self.name}>'

  def serialize(self):
    return {
      'id': self.id,
      'name': self.name,
      'categories': self.categories,
      'stars': self.stars,
      'review_count': self.review_count,
      'address': self.address,
      'city': self.city,
      'state': self.state,
      'postal_code': self.postal_code,
      'latitude': self.latitude,
      'longitude': self.longitude,
      'attributes': self.attributes,
      'hours': self.hours
    }