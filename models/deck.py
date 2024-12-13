'''Deck model for managing Pokemon TCG decks'''

# Third-party imports
from init import db

# Local application imports
from models.format import Format
from models.deckbox import DeckBox


class Deck(db.Model):
    """
    Represents a Pokemon Trading Card Game deck.
    
    Attributes:
        id (int): Primary key for the deck
        name (str): Name of the deck
        description (str): Description of the deck
        format_id (int): Foreign key reference to the format
        deckbox_id (int): Foreign key reference to the deckbox
        deck_cards (relationship): Relationship to associated cards
        format (relationship): Relationship to the deck format
        deckbox (relationship): Relationship to the deck box
        ratings (relationship): Relationship to deck ratings
    """
    
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))
    deckbox_id = db.Column(db.Integer, db.ForeignKey('deckboxes.id'))

    # Database relationships
    deck_cards = db.relationship('DeckCard', back_populates='deck', lazy=True)
    format = db.relationship('Format', backref='decks')
    deckbox = db.relationship('DeckBox', back_populates='decks')
    ratings = db.relationship('Rating', back_populates='deck', lazy='dynamic')

    def __repr__(self):
        return f'<Deck {self.name}>'