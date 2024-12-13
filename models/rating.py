from init import db, ma

# Rating Model
class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)  # Unique rating ID
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)  # FK to Deck
    score = db.Column(db.Integer, nullable=False)  # Rating score (1–5)
    comment = db.Column(db.Text, nullable=True)  # Optional comment about the rating
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # Created time

    # Relationships
    deck = db.relationship('Deck', back_populates='ratings')  # Links to Deck model

