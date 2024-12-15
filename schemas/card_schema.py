'''Schema for serializing and deserializing Pokemon TCG cards'''

from init import ma
from marshmallow import validates, ValidationError
from schemas.cardtype_schema import CardTypeSchema
from schemas.cardset_schema import SetSchema

class CardSchema(ma.Schema):
    cardtype = ma.Nested(CardTypeSchema)
    sets = ma.Nested(SetSchema)
    
    class Meta:
        fields = ('id', 'name', 'cardtype', 'set_id')
        ordered = True
    
    # Relationships
    cardset = ma.relationship("CardSet", backref="cards")

# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

