from init import ma
from models.deckbox import DeckBox

class DeckBoxSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DeckBox

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()

    # Nested relationship to Deck
    decks = ma.Nested("DeckSchema", many=True, only=["id", "name", "format"])
