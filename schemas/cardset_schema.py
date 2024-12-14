'''Schema for serializing and deserializing Pokemon TCG card sets'''

# Third-party imports
from init import ma
from models.cardset import CardSet
from marshmallow import validates, ValidationError
from datetime import datetime

class SetSchema(ma.SQLAlchemySchema):
    """
    Schema for CardSet model serialization.
    
    Attributes:
        id: Set identifier
        name: Set name
        release_date: Set release date
        description: Set description
        cards: Nested relationship to cards in set
        format_restrictions: Nested relationship to format restrictions
    """
    
    class Meta:
        model = CardSet
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    release_date = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    
    # Enhanced relationships
    cards = ma.Nested('CardSchema', many=True, exclude=('set_id',))
    format_restrictions = ma.Nested('FormatRestrictionSchema', many=True)

set_schema = SetSchema()
sets_schema = SetSchema(many=True)
