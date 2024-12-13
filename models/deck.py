from init import db
from models.format import Format
from models.card import Card
from models.deckbox import DeckBox

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))
    deckbox_id = db.Column(db.Integer, db.ForeignKey('deckboxes.id'))
    
    format = db.relationship('Format')
    deckbox = db.relationship('DeckBox')
    cards = db.relationship(
        'DeckCard',
        primaryjoin="Deck.id == DeckCard.deck_id",
        back_populates="deck",
        lazy='dynamic'
    )
    ratings = db.relationship("Rating", back_populates="deck", lazy="dynamic")