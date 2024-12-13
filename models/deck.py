from init import db

class Deck(db.Model):
    __tablename__ = 'decks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'))
    deckbox_id = db.Column(db.Integer, db.ForeignKey('deckboxes.id'))
    
    format = db.relationship('Format')
    deckbox = db.relationship('DeckBox')
    cards = db.relationship('Card', secondary='deck_card', lazy='dynamic')
    ratings = db.relationship("Rating", back_populates="deck", lazy="dynamic")