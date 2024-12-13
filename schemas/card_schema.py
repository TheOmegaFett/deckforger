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

    @validates('name')
    def validate_name(self, value):
        if len(value) < 1:
            raise ValidationError('Name must not be empty')
        if len(value) > 100:
            raise ValidationError('Name must be less than 100 characters')

    @validates('type')
    def validate_type(self, value):
        valid_types = ['grass', 'fire', 'water', 'lightning', 'fighting', 'psychic', 'colorless', 'darkness', 'metal', 'dragon', 'fairy']
        if value.lower() not in valid_types:
            raise ValidationError('Invalid Pokemon card type. Must be one of: ' + ', '.join(valid_types))

    @validates('set_id')
    def validate_set_id(self, value):
        if value <= 0:
            raise ValidationError('Set ID must be a positive integer')