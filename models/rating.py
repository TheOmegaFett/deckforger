'''Rating model for managing Pokemon TCG deck ratings'''

# Third-party imports
from init import db


class Rating(db.Model):
    """
    Represents a rating for a Pokemon Trading Card Game deck.
    
    Attributes:
        id (int): Primary key for the rating
        deck_id (int): Foreign key reference to the rated deck
        score (int): Rating score (1-5)
        comment (str): Optional comment about the rating
        created_at (datetime): Timestamp of rating creation
        deck (relationship): Relationship to the rated deck
    """
    
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Database relationships
    deck = db.relationship('Deck', back_populates='ratings')

    def __repr__(self):
        return f'<Rating {self.deck_id}:{self.score}>'
