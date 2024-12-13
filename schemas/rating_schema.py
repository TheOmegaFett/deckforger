from init import ma
from models.rating import Rating

class RatingSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating

    id = ma.auto_field()
    deck_id = ma.auto_field()
    score = ma.auto_field()
    comment = ma.auto_field()
    created_at = ma.auto_field()

    # Nested relationship to Deck
    deck = ma.Nested("DeckSchema", only=["id", "name"])
