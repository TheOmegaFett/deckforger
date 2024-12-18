'''Controller for managing Pokemon TCG card type operations'''

from flask import Blueprint, jsonify
from sqlalchemy import desc, func, text
from init import db
from models.cardtype import CardType
from models.card import Card
from models.cardset import CardSet
from models.deckcard import DeckCard
from schemas.cardtype_schema import cardtype_schema, cardtypes_schema

cardtype_controller = Blueprint('cardtypes', __name__, url_prefix='/cardtypes')

@cardtype_controller.route('/', methods=['GET'])
def get_all_types():
    """
    Retrieve all card types.
    
    Returns:
        200: List of all card types
        500: Database query failed
    """
    try:
        stmt = db.select(CardType)
        types = db.session.scalars(stmt).all()
        return cardtypes_schema.dump(types), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve card types', 'details': str(e)}), 500

@cardtype_controller.route('/search/<string:name>', methods=['GET'])
def search_by_name(name):
    """
    Search for card types by name.
    
    Parameters:
        name (str): Name pattern to search for
        
    Returns:
        200: List of matching card types
        500: Search operation failed
    """
    try:
        stmt = db.select(CardType).filter(CardType.name.ilike(f'%{name}%'))
        types = db.session.scalars(stmt).all()
        return cardtypes_schema.dump(types), 200
    except Exception as e:
        return jsonify({'error': 'Failed to search card types', 'details': str(e)}), 500

@cardtype_controller.route('/<int:cardtype_id>/cards', methods=['GET'])
def get_cards_by_type(cardtype_id):
    """
    Get all cards of a specific type.
    
    Parameters:
        cardtype_id (int): ID of the card type
        
    Returns:
        200: List of cards of specified type
        404: Card type not found
        500: Query operation failed
    """
    try:
        stmt = db.select(CardType).filter_by(id=cardtype_id)
        card_type = db.session.scalar(stmt)
        if not card_type:
            return jsonify({'error': 'Card type not found'}), 404
            
        return jsonify([{
            'id': card.id,
            'name': card.name,
            'set': card.cardset.name
        } for card in card_type.cards]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve cards', 'details': str(e)}), 500

@cardtype_controller.route('/popularity-in-decks')
def get_type_popularity():
    """
    Get popularity statistics of card types across all decks.
    
    Calculates usage frequency of each card type in all decks by counting
    occurrences in deck compositions.
    
    Returns:
        200: JSON array of card types with their usage counts
        500: Database query failed
    """
    try:
        stmt = (
            db.select(
                CardType,
                func.count(DeckCard.id).label('usage_count')
            )
            .select_from(CardType)
            .join(Card, Card.cardtype_id == CardType.id)
            .join(DeckCard, DeckCard.card_id == Card.id)
            .group_by(CardType.id, CardType.name)
            .order_by(desc('usage_count'))
        )
        
        with db.session.begin():
            results = db.session.execute(stmt).all()
            
        return jsonify([{
            'card_type': cardtype[0].name,
            'usage_count': cardtype[1]
        } for cardtype in results]), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to calculate type popularity',
            'details': str(e)
        }), 500

@cardtype_controller.route('/distribution-by-set', methods=['GET'])
def get_type_distribution():
    """
    Get distribution of types across all sets.
    
    Returns:
        200: Type distribution statistics per set
        500: Distribution calculation failed
    """
    try:
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
    except Exception as e:
        return jsonify({'error': 'Failed to calculate type distribution', 'details': str(e)}), 500