'''Schema for serializing and deserializing Pokemon TCG decks'''

# Third-party imports
from init import ma

# Local application imports
from models.deck import Deck


class DeckSchema(ma.SQLAlchemySchema):
    """
    Schema for Deck model serialization.
    
    Attributes:
        id: Deck identifier
        name: Deck name
        description: Deck description
        format_id: Reference to deck format
        cards: Nested relationship to cards in deck
    """
    
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    format_id = ma.auto_field(required=True)
    cards = ma.Nested('DeckCardSchema', only=['id', 'quantity'], many=True)


deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)
