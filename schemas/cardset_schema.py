'''Schema for serializing and deserializing Pokemon TCG card sets'''

from init import ma
from marshmallow import fields

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
        fields = ('id', 'name', 'code', 'release_date', 'cards')
        ordered = True

    # Relationship
    cards = fields.Nested('CardSchema', many=True, exclude=('cardset',))

cardset_schema = CardSetSchema()
cardsets_schema = CardSetSchema(many=True)
