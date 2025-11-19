class Review:
  def __init__(self, id, user_id, business_id, stars, date, text):
    self.id = id
    self.user_id = user_id
    self.business_id = business_id
    self.stars = stars
    self.date = date
    self.text = text

  def __repr__(self):
    return f'<Review {self.id}>'
  
  def serialize(self):
    return {
      'id': self.id,
      'user_id': self.user_id,
      'business_id': self.business_id,
      'stars': self.stars,
      'date': self.date,
      'text': self.text
    }