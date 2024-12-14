'''Schema for serializing and deserializing Pokemon TCG deck history'''

from init import ma
from marshmallow import validates, ValidationError
from models.deck_history import DeckHistory

class DeckHistorySchema(ma.SQLAlchemySchema):
    """
    Schema for DeckHistory model serialization.
    
    Attributes:
        id: History entry identifier
        deck_id: Reference to modified deck
        change_type: Type of change (CREATE, UPDATE, DELETE)
        changes: JSON record of changes made
        created_at: Change timestamp
    """
    
    class Meta:
        model = DeckHistory
        include_fk = True

    id = ma.auto_field()
    deck_id = ma.auto_field(required=True)
    change_type = ma.auto_field(required=True)
    changes = ma.auto_field(required=True)
    created_at = ma.auto_field(dump_only=True)
    
    # Nested relationship
    decks = ma.Nested('DeckSchema', only=['id', 'name'])

# Schema instances
history_schema = DeckHistorySchema()
histories_schema = DeckHistorySchema(many=True)
