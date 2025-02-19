from init import db
from datetime import datetime

class AIAnalysis(db.Model):
    __tablename__ = 'ai_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    win_rate = db.Column(db.Float)
    total_battles = db.Column(db.Integer)
    average_turns = db.Column(db.Float)
    performance_metrics = db.Column(db.JSON)
    trend_analysis = db.Column(db.JSON)
    
    # Relationships
    deck = db.relationship('Deck', back_populates='analyses')
    
    def __repr__(self):
        return f'<AIAnalysis deck_id={self.deck_id} timestamp={self.timestamp}>'
