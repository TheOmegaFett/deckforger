'''Schema for serializing and deserializing Pokemon TCG cards'''

from init import ma
from marshmallow import validates, ValidationError
from models.card import Card

class CardSchema(ma.SQLAlchemySchema):
    """Base schema for Card model serialization"""
    
    class Meta:
        model = Card
        include_fk = True

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    type = ma.auto_field(required=True)
    set_id = ma.auto_field(required=True)
   

# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

