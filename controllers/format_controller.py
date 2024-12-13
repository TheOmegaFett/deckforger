'''Controller for managing Pokemon TCG game format operations'''

# Third-party imports
from datetime import datetime
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError, validates

# Local application imports
from models.card import Card
from models.cardset import CardSet
from models.deckcard import DeckCard
from models.format import Format
from init import db


format_controller = Blueprint('formats', __name__)


@validates('format_id')
def validate_deck_format(self, format_id):
    """
    Validate deck format legality.
    
    Parameters:
        format_id (int): Format to validate against
        
    Raises:
        ValidationError: If deck contains cards not legal in format
    """
    stmt = (
        db.select(DeckCard, Card, CardSet)
        .join(Card)
        .join(CardSet)
        .filter(DeckCard.deck_id == self.id)
    )
    results = db.session.execute(stmt).all()
    
    standard_date = datetime(2022, 7, 1)
    expanded_date = datetime(2011, 9, 1)
    
    for deck_card, card, card_set in results:
        if format_id == 1:  # Standard
            if card_set.release_date < standard_date:
                raise ValidationError(
                    f'Card {card.name} from set {card_set.name} is not legal in Standard format'
                )
        elif format_id == 2:  # Expanded
            if card_set.release_date < expanded_date:
                raise ValidationError(
                    f'Card {card.name} from set {card_set.name} is not legal in Expanded format'
                )


@format_controller.route('/', methods=['GET'])
def get_formats():
    """
    Retrieve all game formats.
    
    Returns:
        200: List of all formats
    """
    formats = Format.query.all()
    return jsonify([format.to_dict() for format in formats])


@format_controller.route('/<int:format_id>', methods=['GET'])
def get_format(format_id):
    """
    Retrieve a specific format.
    
    Parameters:
        format_id (int): ID of the format to retrieve
        
    Returns:
        200: Format details
        404: Format not found
    """
    format = Format.query.get_or_404(format_id)
    return jsonify(format.to_dict())


@format_controller.route('/', methods=['POST'])
def create_format():
    """
    Create a new game format.
    
    Request Body:
        name (str): Name of the format
        description (str): Description of format rules
        
    Returns:
        201: Format created successfully
        400: Missing required fields
        409: Format name already exists
    """
    data = request.get_json()
    
    if not all(field in data for field in ['name', 'description']):
        return jsonify({'error': 'Missing required fields'}), 400
        
    if Format.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Format name already exists'}), 409

    new_format = Format(
        name=data['name'],
        description=data['description']
    )
    
    db.session.add(new_format)
    db.session.commit()
    
    return jsonify(new_format.to_dict()), 201


@format_controller.route('/<int:format_id>', methods=['PUT'])
def update_format(format_id):
    """
    Update a specific format.
    
    Parameters:
        format_id (int): ID of the format to update
        
    Request Body:
        name (str, optional): New name for the format
        description (str, optional): New description
        
    Returns:
        200: Format updated successfully
        404: Format not found
        409: Format name already exists
    """
    format = Format.query.get_or_404(format_id)
    data = request.get_json()
    
    if 'name' in data:
        existing_format = Format.query.filter_by(name=data['name']).first()
        if existing_format and existing_format.id != format_id:
            return jsonify({'error': 'Format name already exists'}), 409
    
    for field in ['name', 'description']:
        if field in data:
            setattr(format, field, data[field])
    
    db.session.commit()
    return jsonify(format.to_dict())


@format_controller.route('/<int:format_id>', methods=['DELETE'])
def delete_format(format_id):
    """
    Delete a specific format.
    
    Parameters:
        format_id (int): ID of the format to delete
        
    Returns:
        200: Format deleted successfully
        404: Format not found
    """
    format = Format.query.get_or_404(format_id)
    db.session.delete(format)
    db.session.commit()
    return jsonify({'message': 'Format deleted successfully'}), 200