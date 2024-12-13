from init import db, ma


class DeckCard(db.Model):
    __tablename__ = 'deckcards'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

    # Use string references for relationships
    deck = db.relationship("Deck", back_populates="cards")
    card = db.relationship("Card", back_populates="decks")


