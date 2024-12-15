'''Controller for managing Pokemon TCG card set operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from datetime import datetime
from sqlalchemy import func

# Local application imports
from init import db
from models.cardset import CardSet
from models.card import Card
from models.cardtype import CardType
from schemas.cardset_schema import cardset_schema, cardsets_schema

cardset_controller = Blueprint('cardsets', __name__, url_prefix='/cardsets')

@cardset_controller.route('/', methods=['GET'])
def get_all_sets():
    """
    Retrieve all card sets.
    
    Returns:
        200: List of all sets
        500: Database query failed
    """
    try:
        stmt = db.select(CardSet)
        sets = db.session.scalars(stmt).all()
        return cardsets_schema.dump(sets), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve sets', 'details': str(e)}), 500

@cardset_controller.route('/<int:cardset_id>', methods=['GET'])
def get_set(cardset_id):
    """
    Retrieve a specific set by ID.
    
    Parameters:
        cardset_id (int): ID of the set to retrieve
        
    Returns:
        200: Set details
        404: Set not found
        500: Database query failed
    """
    try:
        stmt = db.select(CardSet).filter_by(id=cardset_id)
        set = db.session.scalar(stmt)
        if not set:
            return jsonify({'error': 'Set not found'}), 404
        return cardset_schema.dump(set), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve set', 'details': str(e)}), 500

@cardset_controller.route('/', methods=['POST'])
def create_set():
    """
    Create a new card set.
    
    Request Body:
        name (str): Name of the set
        release_date (date): Release date of the set
        description (str): Description of the set
        
    Returns:
        201: Set created successfully
        409: Set with name already exists
        500: Database operation failed
    """
    try:
        data = request.json
        stmt = db.select(CardSet).filter_by(name=data['name'])
        if db.session.scalar(stmt):
            return jsonify({'error': f'Set \'{data["name"]}\' already exists'}), 409

        new_set = CardSet(
            name=data['name'],
            release_date=data.get('release_date'),
            description=data.get('description')
        )
        db.session.add(new_set)
        db.session.commit()
        return cardset_schema.jsonify(new_set), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create set', 'details': str(e)}), 500

@cardset_controller.route('/<int:cardset_id>', methods=['PUT'])
def update_set(cardset_id):
    """
    Update a specific card set.
    
    Parameters:
        cardset_id (int): ID of the set to update
        
    Request Body:
        name (str, optional): New name for the set
        release_date (date, optional): New release date
        description (str, optional): New description
        
    Returns:
        200: Set updated successfully
        404: Set not found
        500: Database operation failed
    """
    try:
        set_ = db.session.get(CardSet, cardset_id)
        if not set_:
            return jsonify({'error': 'Set not found'}), 404

        data = request.json
        set_.name = data.get('name', set_.name)
        set_.release_date = data.get('release_date', set_.release_date)
        set_.description = data.get('description', set_.description)
        
        db.session.commit()
        return cardset_schema.jsonify(set_), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update set', 'details': str(e)}), 500

@cardset_controller.route('/<int:cardset_id>', methods=['DELETE'])
def delete_set(cardset_id):
    """
    Delete a specific Pokemon card set.
    
    Parameters:
        cardset_id (int): ID of the set to delete
        
    Returns:
        200: Set deleted successfully
        404: Set not found
    """
    set_ = db.session.get(CardSet, cardset_id)
    if not set_:
        return jsonify({'error': 'Set not found'}), 404

    db.session.delete(set_)
    db.session.commit()
    return jsonify({'message': 'Set deleted successfully!'})

@cardset_controller.route('/search/<string:name>', methods=['GET'])
def search_by_name(name):
    """Search for sets by name"""
    stmt = db.select(CardSet).filter(CardSet.name.ilike(f'%{name}%'))
    sets = db.session.scalars(stmt).all()
    return cardsets_schema.dump(sets)

@cardset_controller.route('/<int:cardset_id>/cards', methods=['GET'])
def get_cards_in_set(cardset_id):
    """Get all cards in a specific set"""
    stmt = db.select(CardSet).filter_by(id=cardset_id)
    cardset = db.session.scalar(stmt)
    if not cardset:
        return {'error': 'Set not found'}, 404
    return jsonify([{
        'id': card.id,
        'name': card.name,
        'cardtype': card.cardtype.name
    } for card in cardset.cards])

@cardset_controller.route('/stats/card-distribution', methods=['GET'])
def get_card_distribution():
    """
    Get distribution of cards across sets with type breakdown.
    
    Returns:
        200: Card distribution statistics per set
        500: Database query failed
    """
    try:
        stmt = (
            db.select(
                CardSet.name.label('set_name'),
                CardType.name.label('type_name'),
                func.count(Card.id).label('count')
            )
            .select_from(CardSet)
            .join(Card)
            .join(CardType)
            .group_by(CardSet.name, CardType.name)
            .order_by(CardSet.name)
        )
        
        results = db.session.execute(stmt).all()
        
        distribution = {}
        for result in results:
            set_name = result.set_name
            if set_name not in distribution:
                distribution[set_name] = {'types': {}}
            distribution[set_name]['types'][result.type_name] = result.count
            
        return jsonify(distribution), 200
        
    except Exception as e:
        return jsonify({
            'message': 'Database query failed',
            'error': str(e)
        }), 500    return jsonify(distribution), 200