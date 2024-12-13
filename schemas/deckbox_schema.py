from init import ma
from models.deckbox import DeckBox
from marshmallow import validates, ValidationError

class DeckBoxSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DeckBox

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    decks = ma.Nested("DeckSchema", many=True, only=["id", "name", "format"])

