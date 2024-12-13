'''Schema for serializing and deserializing Pokemon TCG deck ratings'''

# Third-party imports
from init import ma

# Local application imports
from models.rating import Rating


class RatingSchema(ma.SQLAlchemySchema):
    """
    Schema for Rating model serialization.
    
    Attributes:
        id: Rating identifier
        deck_id: Reference to rated deck
        score: Rating score value
        comment: Optional rating comment
        created_at: Rating timestamp
        deck: Nested deck relationship
    """
    
    class Meta:
        model = Rating

    id = ma.auto_field()
    deck_id = ma.auto_field(required=True)
    score = ma.auto_field(required=True)
    comment = ma.auto_field()
    created_at = ma.auto_field()
    deck = ma.Nested('DeckSchema', only=['id', 'name'])


rating_schema = RatingSchema()
ratings_schema = RatingSchema(many=True)
