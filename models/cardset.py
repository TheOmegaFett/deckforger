'''Cardset model for managing Pokemon TCG card sets'''

from init import db


class CardSet(db.Model):
    """
    Represents a card set in the database.
    
    Attributes:
        id (int): Primary key for the set
        name (str): Name of the set, must be unique
        release_date (date): Release date of the set
        description (text): Description of the set
        cards (relationship): Relationship to associated cards in the set
    """
    
    __tablename__ = 'cardsets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    release_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    cards = db.relationship('Card', back_populates='cardset', lazy=True)

    def __repr__(self):
        return f'<Set {self.name}>'