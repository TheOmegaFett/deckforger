from marshmallow import Schema, fields

class AIAnalysisSchema(Schema):
    deck_id = fields.Int(required=True)
    name = fields.Str(required=True)
    total_battles = fields.Int()
    win_rate = fields.Float()
    performance_metrics = fields.Dict()
    trend_analysis = fields.Dict()
    timestamp = fields.DateTime()
# Create and export the schema instances
ai_analysis_schema = AIAnalysisSchema()
ai_analyses_schema = AIAnalysisSchema(many=True)
