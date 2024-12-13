from init import ma
from models.card import Card

class CardSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Card

    id = ma.auto_field()
    name = ma.auto_field()
    type = ma.auto_field()
    set_id = ma.auto_field()
