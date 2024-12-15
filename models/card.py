'''Card model for managing Pokemon TCG cards'''

# Third-party imports
from init import db
from models.cardset import CardSet


class Card(db.Model):
    __tablename__ = 'cards'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cardset_id = db.Column(db.Integer, db.ForeignKey('cardsets.id'), nullable=False)
    cardtype_id = db.Column(db.Integer, db.ForeignKey('cardtypes.id'), nullable=False)
    
    # Relationships
    cardset = db.relationship('CardSet', back_populates='cards')
    cardtype = db.relationship('CardType', back_populates='cards')
    formats = db.relationship('Format', back_populates='cards')

    def __repr__(self):
        return f'<Card {self.name}>'
