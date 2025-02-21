from init import ma
from models.ai_analysis import AIAnalysis

class AIAnalysisSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AIAnalysis
        include_fk = True
        load_instance = True

# Create schema instances for single and multiple records
ai_analysis_schema = AIAnalysisSchema()
ai_analyses_schema = AIAnalysisSchema(many=True)
