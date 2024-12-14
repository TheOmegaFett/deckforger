'''DeckBox model for managing Pokemon TCG deck storage'''

# Third-party imports
from init import db


class DeckBox(db.Model):
    """
    Represents a storage container for Pokemon TCG decks.
    
    Attributes:
        id (int): Primary key for the deck box
        name (str): Name of the deck box
        description (str): Description of the deck box
        decks (relationship): Relationship to stored decks
    """
    
    __tablename__ = 'deckboxes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))

    # Relationships
    decks = db.relationship('Deck', back_populates='deckbox')

    def __repr__(self):
        return f'<DeckBox {self.name}>'