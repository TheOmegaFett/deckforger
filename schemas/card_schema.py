from init import ma
from models.card import Card
from marshmallow import validates, ValidationError

class CardSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Card

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    type = ma.auto_field(required=True)
    set_id = ma.auto_field(required=True)

