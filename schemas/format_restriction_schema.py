'''Schema for serializing and deserializing Pokemon TCG format restrictions'''

from init import ma
from marshmallow import validates, ValidationError
from models.format_restriction import FormatRestriction

class FormatRestrictionSchema(ma.SQLAlchemySchema):
    """
    Schema for FormatRestriction model serialization.
    
    Attributes:
        id: Restriction identifier
        format_id: Reference to game format
        set_id: Reference to card set
        valid_from: Start date of restriction
        valid_until: Optional end date of restriction
    """
    
    class Meta:
        model = FormatRestriction
        include_fk = True

    id = ma.auto_field()
    format_id = ma.auto_field(required=True)
    set_id = ma.auto_field(required=True)
    valid_from = ma.auto_field(required=True)
    valid_until = ma.auto_field()
    
    # Nested relationships
    format = ma.Nested('FormatSchema', only=['id', 'name'])
    card_set = ma.Nested('SetSchema', only=['id', 'name'])

# Schema instances
restriction_schema = FormatRestrictionSchema()
restrictions_schema = FormatRestrictionSchema(many=True)
