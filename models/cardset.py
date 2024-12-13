from init import db

class CardSet(db.Model):
    __tablename__ = "sets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    release_date = db.Column(db.Date, nullable=True)
    description = db.Column(db.Text, nullable=True)

    # Relationship with Card
    cards = db.relationship("Card", back_populates="set", lazy=True)

    def __repr__(self):
        return f"<Set {self.name}>"
