'''Schema for serializing and deserializing Pokemon TCG game formats'''

from init import ma
from models.format import Format


class FormatSchema(ma.SQLAlchemySchema):
    """
    Schema for Format model serialization.
    
    Attributes:
        id: Format identifier
        name: Format name
        description: Format rules description
    """
    
    class Meta:
        model = Format

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()

    # relationships
    start_date = ma.auto_field()    
    decks = ma.Nested('DeckSchema', many=True, only=['id', 'name'])