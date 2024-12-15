'''Schema for CardType serialization'''

from init import ma

class CardTypeSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name')
        ordered = True

cardtype_schema = CardTypeSchema()
cardtypes_schema = CardTypeSchema(many=True)
