from init import db
from models.format import Format
from models.deckbox import DeckBox

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))
    deckbox_id = db.Column(db.Integer, db.ForeignKey('deckboxes.id'))
    
    # Relationships
    format = db.relationship('Format', backref='decks')  # Link to Format
    deckbox = db.relationship('DeckBox', back_populates="decks")  # Link to DeckBox
    cards = db.relationship('DeckCard', back_populates="deck", lazy='dynamic')
    ratings = db.relationship("Rating", back_populates="deck", lazy="dynamic")
