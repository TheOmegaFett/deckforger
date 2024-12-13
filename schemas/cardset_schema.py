from init import ma
from models.cardset import CardSet
from marshmallow import validates, ValidationError
from datetime import datetime

class SetSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CardSet
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    release_date = ma.auto_field(required=True)
    description = ma.auto_field(required=True)
    cards = ma.Nested("CardSchema", many=True, exclude=("set_id",))


set_schema = SetSchema()
sets_schema = SetSchema(many=True)
