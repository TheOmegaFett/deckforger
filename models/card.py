'''Card model for managing Pokemon TCG cards'''

from init import db

class Card(db.Model):
    """
    Represents a Pokemon Trading Card Game card.
    
    This model stores essential information about individual Pokemon cards including
    their name, type, and which set they belong to. It maintains relationships with
    CardType and CardSet models, as well as connecting to decks through DeckCards.
    
    Attributes:
        id (int): Primary key for the card
        name (str): Name of the card
        cardtype_id (int): Foreign key reference to the card type
        cardset_id (int): Foreign key reference to the set
        card_number (str): Number of the card within its set
        cardtype (relationship): Relationship to the card type
        cardset (relationship): Relationship to the parent set
        deck_cards (relationship): Relationship to associated decks
    """
    
    __tablename__ = 'cards'

    # Primary and foreign key columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cardtype_id = db.Column(db.Integer, db.ForeignKey('card_types.id'), nullable=False)
    cardset_id = db.Column(db.Integer, db.ForeignKey('cardsets.id'), nullable=False)
    card_number = db.Column(db.String(20), nullable=True)
    
    # Relationships to other models
    cardtype = db.relationship('CardType', back_populates='cards')
    cardset = db.relationship('CardSet', back_populates='cards')
    deck_cards = db.relationship('DeckCard', back_populates='card')
    
    def __repr__(self):
        """String representation of the Card object"""
        return f'<Card {self.name}>'