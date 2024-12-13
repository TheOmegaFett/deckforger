from init import ma
from models.deck import Deck
from marshmallow import validates, ValidationError

class DeckSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    format = ma.auto_field(required=True)
    cards = ma.Nested("DeckCardSchema", only=["id", "quantity"], many=True)

