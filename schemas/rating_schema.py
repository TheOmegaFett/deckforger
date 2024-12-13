from init import ma
from models.rating import Rating
from marshmallow import validates, ValidationError

class RatingSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Rating

    id = ma.auto_field()
    deck_id = ma.auto_field(required=True)
    score = ma.auto_field(required=True)
    comment = ma.auto_field()
    created_at = ma.auto_field()
    deck = ma.Nested('DeckSchema', only=['id', 'name'])

