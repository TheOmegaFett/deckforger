'''Schema for serializing and deserializing Pokemon TCG cards'''

# Third-party imports
from init import ma
from marshmallow import validates, ValidationError

# Local application imports
from models.card import Card


class CardSchema(ma.SQLAlchemySchema):
    """
    Schema for Card model serialization.
    
    Attributes:
        id: Card identifier
        name: Card name
        type: Card type
        set_id: Reference to card set
    """
    
    class Meta:
        model = Card

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    type = ma.auto_field(required=True)
    set_id = ma.auto_field(required=True)
