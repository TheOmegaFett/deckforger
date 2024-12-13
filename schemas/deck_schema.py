from init import ma
from models.deck import Deck

class DeckSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    format_id = ma.auto_field(required=True)
    cards = ma.Nested("DeckCardSchema", only=["id", "quantity"], many=True)
