from init import db

class Deck(db.Model):
    __tablename__ = 'deck'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    format = db.Column(db.String(50))

    # Foreign Key to DeckBox
    deckbox_id = db.Column(db.Integer, db.ForeignKey('deckbox.id'), nullable=False)

    # Relationships
    deckbox = db.relationship("DeckBox", back_populates="decks")
    cards = db.relationship("DeckCard", back_populates="deck", lazy="dynamic")
    ratings = db.relationship("Rating", back_populates="deck", lazy="dynamic")
