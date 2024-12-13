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
    
    
    
    
    # relationships
    deck_cards = db.relationship('DeckCard', lazy=True)
    format = db.relationship('Format', backref='decks')
    deckbox = db.relationship('DeckBox', back_populates="decks")    ratings = db.relationship("Rating", back_populates="deck", lazy="dynamic")