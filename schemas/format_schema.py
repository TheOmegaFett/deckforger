from init import ma
from models.format import Format

class FormatSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Format
        
    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
