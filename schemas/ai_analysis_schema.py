from marshmallow import Schema, fields

class PerformanceMetricsSchema(Schema):
    average_turns = fields.Float()
    common_winning_cards = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
    matchup_analysis = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))
    suggested_improvements = fields.Dict(keys=fields.Str(), values=fields.List(fields.Str()))

class TrendAnalysisSchema(Schema):
    recent_performance = fields.Str()
    improvement_rate = fields.Float()
    consistency_score = fields.Float()

class DeckAnalysisSchema(Schema):
    deck_id = fields.Int(required=True)
    name = fields.Str(required=True)
    total_battles = fields.Int()
    win_rate = fields.Float()
    performance_metrics = fields.Nested(PerformanceMetricsSchema)
    trend_analysis = fields.Nested(TrendAnalysisSchema)
    timestamp = fields.DateTime(format='iso')

analysis_schema = DeckAnalysisSchema()
analyses_schema = DeckAnalysisSchema(many=True)
