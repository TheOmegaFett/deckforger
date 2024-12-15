'''Schema for serializing and deserializing Pokemon TCG cards'''

from init import ma
from marshmallow import validates, ValidationError, fields, EXCLUDE
from schemas.cardtype_schema import CardTypeSchema
from schemas.cardset_schema import CardSetSchema

class CardSchema(ma.Schema):
   
    
    class Meta:
        fields = ('id', 'name', 'cardtype', 'cardset')
        ordered = True
        unknown = EXCLUDE  # Ignore unknown fields like cardset_id
        
    # Relationships
    cardtype = ma.Nested(CardTypeSchema)
    cardset = ma.Nested(CardSetSchema, exclude=('cards',))
    
# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

