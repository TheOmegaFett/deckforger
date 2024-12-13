from init import db
from models.cardset import CardSet


class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey("sets.id"), nullable=True)

    # Relationships
    set = db.relationship(CardSet, back_populates="cards")
    decks = db.relationship("DeckCard", back_populates="card", lazy="dynamic")

    def __repr__(self):
      return f"<Card {self.name}>"
