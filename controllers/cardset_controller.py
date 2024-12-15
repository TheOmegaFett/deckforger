'''Controller for managing Pokemon TCG card set operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from datetime import datetime

# Local application imports
from init import db
from models.cardset import CardSet
from schemas.cardset_schema import set_schema, sets_schema


cardset_controller = Blueprint('set_controller', __name__)


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
    return set_schema.jsonify(new_set), 201

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
def get_sets():
    """
    Retrieve all Pokemon card sets.
    
    Returns:
        200: List of all sets
    """
    stmt = db.select(CardSet)
    sets = db.session.scalars(stmt).all()
    return sets_schema.jsonify(sets)

@cardset_controller.route('/<int:set_id>', methods=['GET'])
def get_set(set_id):
    """
    Retrieve a specific Pokemon card set by ID.
    
    Parameters:
        set_id (int): ID of the set to retrieve
        
    Returns:
        200: Set details
        404: Set not found
    """
    set_ = db.session.get(CardSet, set_id)
    if not set_:
        return jsonify({'error': 'Set not found'}), 404
    return set_schema.jsonify(set_)

@cardset_controller.route('/<int:set_id>', methods=['PUT'])
def update_set(set_id):
    """
    Update a specific Pokemon card set.
    
    Parameters:
        set_id (int): ID of the set to update
        
    Request Body:
        name (str, optional): New name for the set
        release_date (date, optional): New release date
        description (str, optional): New description
        
    Returns:
        200: Set updated successfully
        404: Set not found
        500: Database operation failed
    """
    set_ = db.session.get(CardSet, set_id)
    if not set_:
        return jsonify({'error': 'Set not found'}), 404

    data = request.json
    set_.name = data.get('name', set_.name)
    set_.release_date = data.get('release_date', set_.release_date)
    set_.description = data.get('description', set_.description)
    db.session.commit()
    return set_schema.jsonify(set_)

@cardset_controller.route('/<int:set_id>', methods=['DELETE'])
def delete_set(set_id):
    """
    Delete a specific Pokemon card set.
    
    Parameters:
        set_id (int): ID of the set to delete
        
    Returns:
        200: Set deleted successfully
        404: Set not found
    """
    set_ = db.session.get(CardSet, set_id)
    if not set_:
        return jsonify({'error': 'Set not found'}), 404

    db.session.delete(set_)
    db.session.commit()
    return jsonify({'message': 'Set deleted successfully!'})

@cardset_controller.route('/search', methods=['GET'])
def search_sets():
    """
    Search for Pokemon card sets using filters.
    
    Search Parameters:
        name (str, optional): Set name to search for
        release_date (date, optional): Filter by release date
        
    Returns:
        200: List of matching sets
    """
    stmt = db.select(CardSet)
    
    if name := request.args.get('name'):
        stmt = stmt.filter(CardSet.name.ilike(f'%{name}%'))
    if release_date := request.args.get('release_date'):
        stmt = stmt.filter(CardSet.release_date == release_date)
        
    sets = db.session.scalars(stmt).all()
    return sets_schema.jsonify(sets)
