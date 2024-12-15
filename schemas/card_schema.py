'''Schema for serializing and deserializing Pokemon TCG cards'''

from dataclasses import fields
from init import ma
from marshmallow import validates, ValidationError
from schemas.cardtype_schema import CardTypeSchema
from schemas.cardset_schema import SetSchema

class CardSchema(ma.Schema):
    cardtype = fields.Nested(CardTypeSchema)
    sets = fields.Nested(CardSetSchema)
    
    class Meta:
        fields = ('id', 'name', 'cardtype', 'set_id', 'sets')
        ordered = True
   

# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

