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

@cardtype_controller.route('/<int:cardtype_id>/cards', methods=['GET'])
def get_cards_by_type(type_id):
    """Get all cards of a specific type"""
    stmt = db.select(CardType).filter_by(id=cardtype_id)
    card_type = db.session.scalar(stmt)
    if not card_type:
        return jsonify({'error': 'Card type not found'}), 404
    return jsonify([{
        'id': card.id,
        'name': card.name,
        'set': card.sets.name
    } for card in card_type.cards])

@cardtype_controller.route('/popularity-in-decks', methods=['GET'])
def get_type_popularity():
    """
    Get popularity of card types across all decks.
    
    Returns:
        200: Card type usage statistics
    """
    stmt = db.select(
        CardType.name,
        func.count(DeckCard.id).label('usage_count')
    ).\
    join(Card).join(DeckCard).\
    group_by(CardType.name).\
    order_by(text('usage_count DESC'))
    
    popularity = db.session.execute(stmt).all()
    return jsonify([{
        'type': p.name,
        'usage_count': p.usage_count
    } for p in popularity]), 200

@cardtype_controller.route('/distribution-by-set', methods=['GET'])
def get_type_distribution():
    """
    Get distribution of types across all sets.
    
    Returns:
        200: Type distribution per set
    """
    stmt = db.select(
        CardType.name,
        CardSet.name.label('set_name'),
        func.count(Card.id).label('card_count')
    ).\
    join(Card).join(CardSet).\
    group_by(CardType.name, CardSet.name)
    
    distribution = db.session.execute(stmt).all()
    return jsonify([{
        'type': d.name,
        'set': d.set_name,
        'count': d.card_count
    } for d in distribution]), 200
