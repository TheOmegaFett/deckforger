from init import db
from models.format import Format

class Deck(db.Model):
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))

    # Relationships
    format = db.relationship('Format', backref='decks')
    deckbox_id = db.Column(db.Integer, db.ForeignKey("deckboxes.id"))
    deckbox = db.relationship("DeckBox", back_populates="decks")
    cards = db.relationship("DeckCard", back_populates="deck", lazy="dynamic")
    ratings = db.relationship("Rating", back_populates="deck", lazy="dynamic")
