'''DeckCard model for managing Pokemon TCG deck card associations'''

# Third-party imports
from init import db


class DeckCard(db.Model):
    """
    Represents the association between Pokemon TCG cards and decks.
    
    Attributes:
        deck_id (int): Foreign key reference to the deck, part of primary key
        card_id (int): Foreign key reference to the card, part of primary key
        variant_id (int): Foreign key reference to the card variant
        quantity (int): Number of copies of the card in the deck
        created_at (DateTime): Timestamp of when the association was created
        deck (relationship): Relationship to the parent deck
        card (relationship): Relationship to the associated card
        variant (relationship): Relationship to the associated card variant
    """
    
    __tablename__ = 'deckcards'

    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey('card_variants.id'))
    quantity = db.Column(db.Integer, nullable=False, default=1)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Database relationships
    deck = db.relationship('Deck', back_populates='deck_cards')
    card = db.relationship('Card', back_populates='decks')
    variant = db.relationship('CardVariant')

    def __repr__(self):
        return f'<DeckCard {self.deck_id}:{self.card_id}>'
