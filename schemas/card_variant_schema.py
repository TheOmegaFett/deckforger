'''Schema for serializing and deserializing Pokemon TCG card variants'''

from init import ma
from marshmallow import validates, ValidationError
from models.card_variant import CardVariant

class CardVariantSchema(ma.SQLAlchemySchema):
    """
    Schema for CardVariant model serialization.
    
    Attributes:
        id: Variant identifier
        card_id: Reference to base card
        rarity: Card rarity level
        collector_number: Set-specific collector number
        is_reverse_holo: Holographic status
        created_at: Creation timestamp
    """
    
    class Meta:
        model = CardVariant
        include_fk = True

    id = ma.auto_field()
    card_id = ma.auto_field(required=True)
    rarity = ma.auto_field(required=True)
    collector_number = ma.auto_field(required=True)
    is_reverse_holo = ma.auto_field()
    created_at = ma.auto_field(dump_only=True)
    
    # Nested relationship
    card = ma.Nested('CardSchema', only=['id', 'name'])

# Schema instances
variant_schema = CardVariantSchema()
variants_schema = CardVariantSchema(many=True)
