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
        version: Deck version
        created_at: Timestamp of deck creation
        updated_at: Timestamp of last deck update
        cards: Nested relationship to cards in deck
        format: Nested relationship to deck format
        deckbox: Nested relationship to deck box
        history: Nested relationship to deck history
        ratings: Nested relationship to deck ratings
    """
    
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    format_id = ma.auto_field(required=True)
    version = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    # Enhanced relationships
    cards = ma.Nested('DeckCardSchema', many=True)
    format = ma.Nested('FormatSchema', only=['id', 'name'])
    deckbox = ma.Nested('DeckBoxSchema', only=['id', 'name'])
    history = ma.Nested('DeckHistorySchema', many=True)
    ratings = ma.Nested('RatingSchema', many=True)


deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)
