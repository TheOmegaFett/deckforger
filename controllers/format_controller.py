'''Controller for managing Pokemon TCG game format operations'''

from datetime import datetime
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError, validates
from models import card
from models.card import Card
from models.cardset import CardSet
from models.deck import Deck
from models.deckcard import DeckCard
from models.format import Format
from init import db

format_controller = Blueprint('formats', __name__)

@format_controller.route('/', methods=['GET'])
def get_formats():
    """
    Retrieve all game formats.
    
    Returns:
        200: List of all formats
        500: Database query failed
    """
    try:
        stmt = db.select(Format)
        formats = db.session.scalars(stmt).all()
        return jsonify([format.to_dict() for format in formats]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve formats', 'details': str(e)}), 500

@format_controller.route('/<int:format_id>', methods=['GET'])
def get_format(format_id):
    """
    Retrieve a specific format.
    
    Parameters:
        format_id (int): ID of the format to retrieve
        
    Returns:
        200: Format details
        404: Format not found
        500: Database query failed
    """
    try:
        format = db.session.get(Format, format_id)
        if not format:
            return jsonify({'error': 'Format not found'}), 404
        return jsonify(format.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve format', 'details': str(e)}), 500

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
        500: Database operation failed
    """
    try:
        data = request.get_json()
        
        if not all(field in data for field in ['name', 'description']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        stmt = db.select(Format).filter_by(name=data['name'])
        if db.session.scalar(stmt):
            return jsonify({'error': 'Format name already exists'}), 409

        new_format = Format(
            name=data['name'],
            description=data['description'],
            start_date=data['start_date']
        )
        
        db.session.add(new_format)
        db.session.commit()
        
        return jsonify(new_format.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create format', 'details': str(e)}), 500

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
        500: Database operation failed
    """
    try:
        format = db.session.get(Format, format_id)
        if not format:
            return jsonify({'error': 'Format not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            stmt = db.select(Format).filter_by(name=data['name'])
            existing_format = db.session.scalar(stmt)
            if existing_format and existing_format.id != format_id:
                return jsonify({'error': 'Format name already exists'}), 409
        
        for field in ['name', 'description']:
            if field in data:
                setattr(format, field, data[field])
        
        db.session.commit()
        return jsonify(format.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update format', 'details': str(e)}), 500

@format_controller.route('/<int:format_id>', methods=['DELETE'])
def delete_format(format_id):
    """
    Delete a specific format.
    
    Parameters:
        format_id (int): ID of the format to delete
        
    Returns:
        200: Format deleted successfully
        404: Format not found
        500: Database operation failed
    """
    try:
        format = db.session.get(Format, format_id)
        if not format:
            return jsonify({'error': 'Format not found'}), 404

        db.session.delete(format)
        db.session.commit()
        return jsonify({'message': 'Format deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete format', 'details': str(e)}), 500

@format_controller.route('/<int:format_id>/validate', methods=['POST'])
def validate_format_legality(format_id):
    """
    Validate deck legality for a specific format.
    
    Parameters:
        format_id (int): Format to validate against
        
    Request Body:
        deck_id (int): ID of deck to validate
        
    Returns:
        200: Deck is legal in format
        400: Deck violates format rules
        404: Format not found
        500: Validation failed
    """
    try:
        data = request.get_json()
        deck_id = data.get('deck_id')
        
        if not deck_id:
            return jsonify({'error': 'Missing deck_id in request'}), 400
            
        format = db.session.get(Format, format_id)
        if not format:
            return jsonify({'error': 'Format not found'}), 404
            
      
        validate_deck_format(deck_id, format_id)
        
        return jsonify({'message': 'Deck is legal in this format'}), 200
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Validation failed', 'details': str(e)}), 500
    
def validate_deck_format(deck_id, format_id):
    """
    Validates if a deck is legal in a given format based on card release dates
    
    Args:
        deck_id (int): ID of the deck to validate
        format_id (int): ID of the format to validate against
        
    Raises:
        ValidationError: If deck contains cards outside format's date range
    """
    deck = db.session.get(Deck, deck_id)
    format = db.session.get(Format, format_id)
    
    if not deck:
        raise ValidationError("Deck not found")
    if not format:
        raise ValidationError("Format not found")
        
    # Get oldest card's release date from the deck
    stmt = db.select(CardSet.release_date)\
        .join(Card)\
        .join(DeckCard)\
        .filter(DeckCard.deck_id == deck_id)\
        .order_by(CardSet.release_date.asc())\
        .limit(1)
        
    oldest_card_date = db.session.scalar(stmt)
    
    # Convert format.start_date to datetime for comparison
    format_start_datetime = datetime.combine(format.start_date, datetime.min.time())
    
    # Check if oldest card is within format's date range
    if oldest_card_date < format_start_datetime:
        raise ValidationError(f"Deck contains cards released before format's start date: {format.start_date}")    raise ValidationError(f"Card {card.name} is from a set not legal in this format")