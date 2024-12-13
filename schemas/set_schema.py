from init import ma
from models.cardset import CardSet

class SetSchema(ma.SQLAlchemySchema):
    class Meta:
        model = CardSet
        load_instance = True

    id = ma.auto_field()
    name = ma.auto_field()
    release_date = ma.auto_field()
    description = ma.auto_field()
    # Nested relationship
    cards = ma.Nested("CardSchema", many=True, exclude=("set_id",))

# Instantiate schemas
set_schema = SetSchema()
sets_schema = SetSchema(many=True)
