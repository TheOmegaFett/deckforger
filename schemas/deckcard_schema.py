'''Schema for serializing and deserializing Pokemon TCG deck card associations'''

# Third-party imports
from init import ma

# Local application imports
from models.deckcard import DeckCard


class DeckCardSchema(ma.SQLAlchemySchema):
    """
    Schema for DeckCard model serialization.
    
    Attributes:
        id: DeckCard identifier
        deck_id: Reference to parent deck
        card_id: Reference to associated card
        quantity: Number of copies of the card
        deck: Nested deck relationship
        card: Nested card relationship
    """
    
    class Meta:
        model = DeckCard

    id = ma.auto_field()
    deck_id = ma.auto_field(required=True)
    card_id = ma.auto_field(required=True)
    quantity = ma.auto_field(required=True)
    decks = ma.Nested('DeckSchema', only=['id', 'name'])
    cards = ma.Nested('CardSchema', only=['id', 'name', 'type'])


deckcard_schema = DeckCardSchema()
deckcards_schema = DeckCardSchema(many=True)
