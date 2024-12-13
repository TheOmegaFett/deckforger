from init import db

class DeckBox(db.Model):
    __tablename__ = 'deckbox'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Relationship to Deck
    decks = db.relationship('Deck', back_populates='deckbox', lazy=True)
