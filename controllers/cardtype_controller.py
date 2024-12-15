from flask import Blueprint, jsonify
from init import db
from models.cardtype import CardType
from schemas.cardtype_schema import cardtypes_schema

cardtype_controller = Blueprint('cardtypes', __name__, url_prefix='/cardtypes')

@cardtype_controller.route('/', methods=['GET'])
def get_all_types():
    """Get all card types"""
    stmt = db.select(CardType)
    types = db.session.scalars(stmt).all()
    return cardtypes_schema.dump(types)

@cardtype_controller.route('/search/<string:name>', methods=['GET'])
def search_by_name(name):
    """Search for types by name"""
    stmt = db.select(CardType).filter(CardType.name.ilike(f'%{name}%'))
    types = db.session.scalars(stmt).all()
    return cardtypes_schema.dump(types)

@cardtype_controller.route('/<int:type_id>/cards', methods=['GET'])
def get_cards_by_type(type_id):
    """Get all cards of a specific type"""
    stmt = db.select(CardType).filter_by(id=type_id)
    card_type = db.session.scalar(stmt)
    if not card_type:
        return jsonify({'error': 'Card type not found'}), 404
    return jsonify([{
        'id': card.id,
        'name': card.name,
        'set': card.sets.name
    } for card in card_type.cards])
