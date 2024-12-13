from init import ma
from models.deckcard import DeckCard
from schemas.deck_schema import DeckSchema
from schemas.card_schema import CardSchema

class DeckCardSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DeckCard

    id = ma.auto_field()
    deck_id = ma.auto_field()
    card_id = ma.auto_field()
    quantity = ma.auto_field()

    deck = ma.Nested(DeckSchema, only=["id", "name"])
    card = ma.Nested(CardSchema, only=["id", "name", "type"])
