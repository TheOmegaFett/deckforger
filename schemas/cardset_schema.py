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

    @validates('name')
    def validate_name(self, value):
        if len(value) < 1:
            raise ValidationError('Set name must not be empty')
        if len(value) > 100:
            raise ValidationError('Set name must be less than 100 characters')

    @validates('release_date')
    def validate_release_date(self, value):
        if value > datetime.now():
            raise ValidationError('Release date cannot be in the future')

set_schema = SetSchema()
sets_schema = SetSchema(many=True)
