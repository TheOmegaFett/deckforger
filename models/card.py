'''Card model for managing Pokemon TCG cards'''

# Third-party imports
from init import db
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
   
    

    # Relationships
    sets = db.relationship(CardSet, back_populates='cards')
    deck_cards = db.relationship('DeckCard', back_populates='card')

    def __repr__(self):
        return f'<Card {self.name}>'

