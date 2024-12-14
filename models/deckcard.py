'''DeckCard model for managing Pokemon TCG deck card associations'''

# Third-party imports
from init import db

class DeckCard(db.Model):
    __tablename__ = 'deckcards'
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Relationships
    deck = db.relationship('Deck', back_populates='deck_cards')
    card = db.relationship('Card', back_populates='deck_cards')
    
    
    def __repr__(self):
        return f'<DeckCard {self.deck_id}:{self.card_id}>'
