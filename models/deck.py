'''Deck model for managing Pokemon TCG decks'''

from init import db


class Deck(db.Model):
    """
    Represents a Pokemon Trading Card Game deck.
    
    Attributes:
        id (int): Primary key for the deck
        name (str): Name of the deck
        description (str): Description of the deck
        format_id (int): Foreign key reference to the format
        deckbox_id (int): Foreign key reference to the deckbox
        created_at (datetime): Timestamp of deck creation
    """
    
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))
    deckbox_id = db.Column(db.Integer, db.ForeignKey('deckboxes.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    # Relationships
    deck_cards = db.relationship('DeckCard', back_populates='deck')
    deckbox = db.relationship('DeckBox', back_populates='decks')
    rating = db.relationship('Rating', back_populates='deck', lazy='dynamic')
    battlelogs = db.relationship('Battlelog', back_populates='deck')

    def __repr__(self):
        return f'<Deck {self.name}>'