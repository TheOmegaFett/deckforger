'''Schema for serializing and deserializing Pokemon TCG cards'''

from init import ma
from marshmallow import EXCLUDE
from schemas.cardtype_schema import CardTypeSchema
from schemas.cardset_schema import CardSetSchema

class CardSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'cardtype', 'cardset', 'card_number')
        ordered = True
        unknown = EXCLUDE
        
    # Relationships
    cardtype = ma.Nested(CardTypeSchema)
    cardset = ma.Nested(CardSetSchema, exclude=('cards',))
    
# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

