'''Schema for serializing and deserializing Pokemon TCG decks'''

from init import ma
from models.deck import Deck


class DeckSchema(ma.SQLAlchemySchema):
    """
    Schema for Deck model serialization.
    
    Attributes:
        id: Deck identifier
        name: Deck name
        description: Deck description
        format_id: Reference to deck format
        created_at: Timestamp of deck creation
        updated_at: Timestamp of last deck update
        cards: Nested relationship to cards in deck
        deckbox: Nested relationship to deck box
        ratings: Nested relationship to deck ratings
    """
    
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    format_id = ma.auto_field(required=True)
    created_at = ma.auto_field(dump_only=True)
    updated_at = ma.auto_field(dump_only=True)
    
    #  relationships
    cards = ma.Nested('DeckCardSchema', many=True)
    deckbox = ma.Nested('DeckBoxSchema', only=['id', 'name'])
    ratings = ma.Nested('RatingSchema', many=True)


deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)
