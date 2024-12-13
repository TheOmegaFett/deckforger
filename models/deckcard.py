'''DeckCard model for managing Pokemon TCG deck card associations'''

# Third-party imports
from init import db


class DeckCard(db.Model):
    """
    Represents the association between Pokemon TCG cards and decks.
    
    Attributes:
        id (int): Primary key for the deck card association
        deck_id (int): Foreign key reference to the deck
        card_id (int): Foreign key reference to the card
        quantity (int): Number of copies of the card in the deck
        deck (relationship): Relationship to the parent deck
        card (relationship): Relationship to the associated card
    """
    
    __tablename__ = 'deckcards'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Database relationships
    deck = db.relationship('Deck', back_populates='deck_cards')
    card = db.relationship('Card', back_populates='decks')

    def __repr__(self):
        return f'<DeckCard {self.deck_id}:{self.card_id}>'
