from init import db

class Format(db.Model):
    __tablename__ = 'formats'
    
    format_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    
    # Relationship with decks
    decks = db.relationship('Deck', back_populates='format', lazy='dynamic')
