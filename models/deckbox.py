from init import db

class DeckBox(db.Model):
    __tablename__ = 'deckboxes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    
    # Relationship without overlaps
    decks = db.relationship('Deck', back_populates='deckbox', lazy='dynamic')
