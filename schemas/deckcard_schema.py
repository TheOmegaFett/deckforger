from init import ma
from models.deckcard import DeckCard
from marshmallow import validates, ValidationError

class DeckCardSchema(ma.SQLAlchemySchema):
    class Meta:
        model = DeckCard

    id = ma.auto_field()
    deck_id = ma.auto_field(required=True)
    card_id = ma.auto_field(required=True)
    quantity = ma.auto_field(required=True)
    deck = ma.Nested("DeckSchema", only=["id", "name"])
    card = ma.Nested("CardSchema", only=["id", "name", "type"])

    @validates('quantity')
    def validate_quantity(self, value):
        if value < 1:
            raise ValidationError('Quantity must be at least 1')
        if value > 4:
            raise ValidationError('Maximum 4 copies of a card allowed per deck')
