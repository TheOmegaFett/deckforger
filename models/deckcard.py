'''DeckCard model for managing Pokemon TCG deck card associations'''

from init import db

class DeckCard(db.Model):
    """
    Represents the association between decks and cards, tracking card quantities in decks.
    
    This model manages the many-to-many relationship between Deck and Card models,
    allowing cards to be included in multiple decks with specific quantities.
    
    Attributes:
        id (int): Primary key
        deck_id (int): Foreign key to the deck containing the card
        card_id (int): Foreign key to the card being included
        quantity (int): Number of copies of this card in the deck
        
    Relationships:
        deck: Reference to the parent Deck
        card: Reference to the associated Card
    """
    
    __tablename__ = 'deckcards'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    deck = db.relationship('Deck', back_populates='deck_cards')
    card = db.relationship('Card', back_populates='deck_cards')
    
    def __repr__(self):
        """String representation of the DeckCard."""
        return f'<DeckCard {self.deck_id}:{self.card_id}>'
