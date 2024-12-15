from flask import Blueprint, jsonify
from init import db
from models.cardtype import CardType
from schemas.cardtype_schema import cardtypes_schema

cardtype_controller = Blueprint('cardtypes', __name__, url_prefix='/cardtypes')

@cardtype_controller.route('/', methods=['GET'])
def get_all_types():
    """Get all card types"""
    types = CardType.query.all()
    return cardtypes_schema.dump(types)

@cardtype_controller.route('/search/<string:name>', methods=['GET'])
def search_by_name(name):
    """Search for types by name"""
    types = CardType.query.filter(CardType.name.ilike(f'%{name}%')).all()
    return cardtypes_schema.dump(types)

@cardtype_controller.route('/<int:type_id>/cards', methods=['GET'])
def get_cards_by_type(type_id):
    """Get all cards of a specific type"""
    card_type = CardType.query.get_or_404(type_id)
    return jsonify([{
        'id': card.id,
        'name': card.name,
        'set': card.sets.name
    } for card in card_type.cards])
