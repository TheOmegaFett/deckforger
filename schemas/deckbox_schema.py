'''Schema for serializing and deserializing Pokemon TCG deck boxes'''

# Third-party imports
from init import ma
from marshmallow import validates, ValidationError

# Local application imports
from models.deckbox import DeckBox


class DeckBoxSchema(ma.SQLAlchemySchema):
    """
    Schema for DeckBox model serialization.
    
    Attributes:
        id: DeckBox identifier
        name: DeckBox name
        description: DeckBox description
        decks: Nested relationship to stored decks
    """
    
    class Meta:
        model = DeckBox

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    
    # Enhanced relationships with version tracking
    decks = ma.Nested('DeckSchema', many=True, only=[
        'id', 
        'name', 
        'format',
        'version',
        'created_at'
    ])


deckbox_schema = DeckBoxSchema()
deckboxes_schema = DeckBoxSchema(many=True)
