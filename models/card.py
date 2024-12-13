'''Card model for managing Pokemon TCG cards'''

# Third-party imports
from init import db

# Local application imports
from models.cardset import CardSet


class Card(db.Model):
    """
    Represents a Pokemon Trading Card Game card.
    
    Attributes:
        id (int): Primary key for the card
        name (str): Name of the card
        type (str): Card type (Pokemon, Trainer, Energy)
        set_id (int): Foreign key reference to the set
        set (relationship): Relationship to the parent set
        decks (relationship): Relationship to associated decks
    """
    
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'), nullable=False)

    # Database relationships
    set = db.relationship(CardSet, back_populates='cards')
    decks = db.relationship('DeckCards', back_populates='cards', lazy='dynamic')

    def __repr__(self):
        return f'<Card {self.name}>'