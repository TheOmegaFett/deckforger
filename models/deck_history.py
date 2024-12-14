from init import db
from datetime import datetime

class DeckHistory(db.Model):
    __tablename__ = 'deck_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    change_type = db.Column(db.String(50))  # CREATE, UPDATE, DELETE
    changes = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    deck = db.relationship('Deck', back_populates='history')
