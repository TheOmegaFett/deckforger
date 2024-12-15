'''Schema for serializing and deserializing Pokemon TCG cards'''

from init import ma
from marshmallow import validates, ValidationError, fields
from schemas.cardtype_schema import CardTypeSchema
from schemas.cardset_schema import CardSetSchema

class CardSchema(ma.Schema):
    cardtype = ma.Nested(CardTypeSchema)
    cardset = ma.Nested(CardSetSchema)
    
    class Meta:
        fields = ('id', 'name', 'cardtype', 'cardset')
        ordered = True
    
    # Relationships
    cardtype = ma.Nested(CardTypeSchema)
    cardset = ma.Nested(CardSetSchema)
    
# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

