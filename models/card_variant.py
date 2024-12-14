from init import db
from datetime import datetime

class CardVariant(db.Model):
    __tablename__ = 'card_variants'
    
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    rarity = db.Column(db.String(50))
    collector_number = db.Column(db.String(20))
    is_reverse_holo = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Using a more specific backref name
    card = db.relationship('Card', backref='card_variants')
