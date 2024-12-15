'''Schema for serializing and deserializing Pokemon TCG cards'''

from dataclasses import fields
from init import ma
from marshmallow import validates, ValidationError
from schemas.cardtype_schema import CardTypeSchema
from schemas.cardset_schema import SetSchema

class CardSchema(ma.Schema):
    type = fields.Nested(CardTypeSchema)
    sets = fields.Nested(SetSchema)
    
    class Meta:
        fields = ('id', 'name', 'type', 'set_id', 'sets')
        ordered = True
   

# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

