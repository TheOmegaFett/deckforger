from init import ma
from models.deckcard import DeckCard

class DeckCardSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DeckCard

    id = ma.auto_field()
    deck_id = ma.auto_field(required=True)
    card_id = ma.auto_field(required=True)
    quantity = ma.auto_field(required=True)
    deck = ma.Nested('DeckSchema', only=['id', 'name'])
    card = ma.Nested('CardSchema', only=['id', 'name', 'type'])

