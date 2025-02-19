
from marshmallow import Schema, fields

class AnalysesSchema(Schema):
    """Schema for handling analyses data"""
    
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    # Analysis specific fields
    data = fields.Dict()
    status = fields.Str()
    result = fields.Dict()
    
    class Meta:
        ordered = True

# You can create additional schemas for specific analysis types
class DetailedAnalysisSchema(AnalysesSchema):
    """Schema for detailed analysis data"""
    
    description = fields.Str()
    parameters = fields.Dict()
    metadata = fields.Dict()

# Create instances if needed
analyses_schema = AnalysesSchema()
analyses_schema_many = AnalysesSchema(many=True)
detailed_analysis_schema = DetailedAnalysisSchema()
