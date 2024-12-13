from init import ma
from models.deck import Deck

class DeckSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    format = ma.auto_field()
    cards = ma.Nested("DeckCardSchema", only=["id", "quantity"], many=True)
