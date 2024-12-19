'''Schema for serializing and deserializing Pokemon TCG battle logs'''

from init import ma
from marshmallow import EXCLUDE

class BattlelogSchema(ma.Schema):
    class Meta:
        fields = ('id', 'deck_id', 'win_loss', 'total_turns', 'most_used_cards', 'key_synergy_cards', 'damage_done', 'damage_taken')
        ordered = True
        unknown = EXCLUDE

# Schema instances
battlelog_schema = BattlelogSchema()
battlelogs_schema = BattlelogSchema(many=True)
