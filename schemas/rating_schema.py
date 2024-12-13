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
    deck = ma.Nested("DeckSchema", only=["id", "name"])

    @validates('score')
    def validate_score(self, value):
        if not 1 <= value <= 5:
            raise ValidationError('Score must be between 1 and 5')

    @validates('comment')
    def validate_comment(self, value):
        if value and len(value) > 500:
            raise ValidationError('Comment must be less than 500 characters')
