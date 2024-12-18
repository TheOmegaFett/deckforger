'''Schema for serializing and deserializing Pokemon TCG card sets'''

from init import ma
from models.cardset import CardSet

class CardSetSchema(ma.SQLAlchemySchema):
    """
    Schema for CardSet model serialization.
    
    Attributes:
        id: Set identifier
        name: Set name
        release_date: Set release date
        description: Set description
        cards: Nested relationship to cards in set
    """
    
    class Meta:
        model = CardSet
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    release_date = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    
    # Relationships
    cards = ma.Nested('CardSchema', many=True, exclude=('cardset_id',))

cardset_schema = CardSetSchema()
cardsets_schema = CardSetSchema(many=True)
