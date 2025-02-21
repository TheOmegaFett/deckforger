from init import ma
from models.ai_analysis import AIAnalysis

class AnalysesSchema(ma.SQLAlchemySchema):
    class Meta:
        model = AIAnalysis
    
    id = ma.auto_field()
    deck_id = ma.auto_field()
    timestamp = ma.auto_field()
    win_rate = ma.auto_field()
    total_battles = ma.auto_field()
    average_turns = ma.auto_field()
    performance_metrics = ma.auto_field()
    trend_analysis = ma.auto_field()

# Create schema instances
analysis_schema = AnalysesSchema()
analyses_schema = AnalysesSchema(many=True)
