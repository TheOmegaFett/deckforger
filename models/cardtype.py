'''CardType model for managing Pokemon TCG card types'''

from init import db

class CardType(db.Model):
    """
    Represents a Pokemon Trading Card Game card type.
    
    Attributes:
        id (int): Primary key for the type
        name (str): Name of the type (Fire, Water, etc)
        cards (relationship): Cards of this type
    """
    
    __tablename__ = 'card_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    
    # Relationships
    cards = db.relationship('Card', back_populates='type')

    def __repr__(self):
        return f'<CardType {self.name}>'