'''Controller for managing Pokemon TCG card set operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from datetime import datetime

# Local application imports
from init import db
from models.cardset import CardSet
from schemas.cardset_schema import cardset_schema, cardsets_schema


cardset_controller = Blueprint('cardsets', __name__, url_prefix='/cardsets')



@validates('name')
def validate_name(self, value):
    if len(value) < 1:
        raise ValidationError('Set name must not be empty')
    if len(value) > 100:
        raise ValidationError('Set name must be less than 100 characters')

@validates('release_date')
def validate_release_date(self, value):
    try:
        release_date = datetime.strptime(value, '%Y-%m-%d')
    except (ValueError, TypeError):
        raise ValidationError('Invalid date format. Use YYYY-MM-DD')

@cardset_controller.route('/', methods=['GET'])
def get_all_sets():
    """Get all card sets"""
    stmt = db.select(CardSet)
    sets = db.session.scalars(stmt).all()
    return cardsets_schema.dump(sets)

@cardset_controller.route('/<int:cardset_id>', methods=['GET'])
def get_set(cardset_id):
    """Get a specific set by ID"""
    stmt = db.select(CardSet).filter_by(id=cardset_id)
    set = db.session.scalar(stmt)
    if not set:
        return {'error': 'Set not found'}, 404
    return cardset_schema.dump(set)

@cardset_controller.route('/', methods=['POST'])
def create_set():
    """
    Create a new Pokemon card set.
    
    Request Body:
        name (str): Name of the set
        release_date (date): Release date of the set
        description (str): Description of the set
        
    Returns:
        201: Set created successfully
        400: Missing required fields
        409: Set with name already exists
    """
    data = request.json

    # Check for existing set with same name
    stmt = db.select(CardSet).filter_by(name=data['name'])
    existing_set = db.session.scalar(stmt)
    if existing_set:
        return jsonify({'error': f'Set \'{data["name"]}\' already exists'}), 409

    new_set = CardSet(
        name=data['name'],
        release_date=data.get('release_date'),
        description=data.get('description')
    )
    db.session.add(new_set)
    db.session.commit()
    return cardset_schema.jsonify(new_set), 201


@cardset_controller.route('/<int:cardset_id>', methods=['PUT'])
def update_set(cardset_id):
    """
    Update a specific Pokemon card set.
    
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
    set_ = db.session.get(CardSet, cardset_id)
    if not set_:
        return jsonify({'error': 'Set not found'}), 404

    data = request.json
    set_.name = data.get('name', set_.name)
    set_.release_date = data.get('release_date', set_.release_date)
    set_.description = data.get('description', set_.description)
    db.session.commit()
    return cardset_schema.jsonify(set_)

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
    """
    # Query to get card type distribution per set
    stmt = (
        db.select(
            CardSet.name.label('set_name'),
            CardType.name.label('type_name'),
            func.count(Card.id).label('count')
        )
        .join(Card, CardSet.id == Card.cardset_id)
        .join(CardType, Card.cardtype_id == CardType.id)
        .group_by(CardSet.name, CardType.name)
        .order_by(CardSet.name)
    )
    
    results = db.session.execute(stmt).all()
    
    # Organize results by set
    distribution = {}
    for result in results:
        set_name = result.set_name
        if set_name not in distribution:
            distribution[set_name] = {'types': {}}
        distribution[set_name]['types'][result.type_name] = result.count
        
    return jsonify(distribution), 200