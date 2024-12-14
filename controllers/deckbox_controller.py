'''Controller for managing Pokemon TCG deck box operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates

# Local application imports
from init import db
from models.deckbox import DeckBox
from models.deck import Deck
from schemas.deckbox_schema import DeckBoxSchema
from schemas.deck_schema import DeckSchema


# Blueprint and Schema Setup
deckbox_controller = Blueprint('deckbox_controller', __name__)
deckbox_schema = DeckBoxSchema()
deckboxes_schema = DeckBoxSchema(many=True)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)


@validates('name')
def validate_name(self, value):
    """
    Validate deckbox name length.
    
    Parameters:
        value (str): Name to validate
        
    Raises:
        ValidationError: If name is empty or too long
    """
    if len(value) < 1:
        raise ValidationError('Deckbox name must not be empty')
    if len(value) > 50:
        raise ValidationError('Deckbox name must be less than 50 characters')


@deckbox_controller.route('/', methods=['POST'])
def create_deckbox():
    """
    Create a new deck box.
    
    Request Body:
        name (str): Name of the deck box
        description (str, optional): Description of the deck box
        
    Returns:
        201: Deck box created successfully
        400: Invalid input data
    """
    data = request.json
    deckbox = DeckBox(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(deckbox)
    db.session.commit()
    return deckbox_schema.jsonify(deckbox), 201


@deckbox_controller.route('/', methods=['GET'])
def read_all_deckboxes():
    """
    Retrieve all deck boxes.
    
    Returns:
        200: List of all deck boxes
    """
    stmt = db.select(DeckBox)
    deckboxes = db.session.scalars(stmt).all()
    return deckboxes_schema.jsonify(deckboxes)


@deckbox_controller.route('/<int:deckbox_id>', methods=['GET'])
def read_one_deckbox(deckbox_id):
    """
    Retrieve a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to retrieve
        
    Returns:
        200: Deck box details
        404: Deck box not found
    """
    deckbox = db.session.get(DeckBox, deckbox_id)
    if not deckbox:
        return jsonify({'error': 'DeckBox not found'}), 404
    return deckbox_schema.jsonify(deckbox)


@deckbox_controller.route('/<int:deckbox_id>', methods=['PUT'])
def update_deckbox(deckbox_id):
    """
    Update a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to update
        
    Request Body:
        name (str, optional): New name for the deck box
        description (str, optional): New description
        
    Returns:
        200: Deck box updated successfully
        404: Deck box not found
    """
    deckbox = db.session.get(DeckBox, deckbox_id)
    if not deckbox:
        return jsonify({'error': 'DeckBox not found'}), 404

    data = request.json
    deckbox.name = data.get('name', deckbox.name)
    deckbox.description = data.get('description', deckbox.description)
    db.session.commit()
    return deckbox_schema.jsonify(deckbox)


@deckbox_controller.route('/<int:deckbox_id>', methods=['DELETE'])
def delete_deckbox(deckbox_id):
    """
    Delete a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to delete
        
    Returns:
        200: Deck box deleted successfully
        404: Deck box not found
    """
    deckbox = db.session.get(DeckBox, deckbox_id)
    if not deckbox:
        return jsonify({'error': 'DeckBox not found'}), 404

    db.session.delete(deckbox)
    db.session.commit()
    return jsonify({'message': 'DeckBox deleted successfully!'})


@deckbox_controller.route('/<int:deckbox_id>/decks', methods=['GET'])
def show_decks_in_deckbox(deckbox_id):
    """
    List all decks in a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to list decks from
        
    Returns:
        200: List of decks in the deck box
        404: Deck box not found
    """
    deckbox = db.session.get(DeckBox, deckbox_id)
    if not deckbox:
        return jsonify({'error': 'DeckBox not found'}), 404

    return decks_schema.jsonify(deckbox.decks)


@deckbox_controller.route('/<int:deckbox_id>/decks', methods=['POST'])
def add_deck_to_deckbox(deckbox_id):
    """
    Add a new deck to a deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to add deck to
        
    Request Body:
        name (str): Name of the new deck
        description (str, optional): Description of the deck
        format (str): Format of the deck
        
    Returns:
        201: Deck added successfully
        404: Deck box not found
    """
    deckbox = db.session.get(DeckBox, deckbox_id)
    if not deckbox:
        return jsonify({'error': 'DeckBox not found'}), 404

    data = request.json
    deck = Deck(
        name=data['name'],
        description=data.get('description', ''),
        format=data.get('format', 'Standard'),
        deckbox_id=deckbox_id
    )
    db.session.add(deck)
    db.session.commit()

    return deck_schema.jsonify(deck), 201


@deckbox_controller.route('/<int:deckbox_id>/decks/<int:deck_id>', methods=['DELETE'])
def remove_deck_from_deckbox(deckbox_id, deck_id):
    """
    Remove a deck from a deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box containing the deck
        deck_id (int): ID of the deck to remove
        
    Returns:
        200: Deck removed successfully
        404: Deck box or deck not found
    """
    deckbox = db.session.get(DeckBox, deckbox_id)
    if not deckbox:
        return jsonify({'error': 'DeckBox not found'}), 404

    stmt = db.select(Deck).filter_by(id=deck_id, deckbox_id=deckbox_id)
    deck = db.session.scalar(stmt)
    if not deck:
        return jsonify({'error': 'Deck not found in this DeckBox'}), 404

    db.session.delete(deck)
    db.session.commit()
    return jsonify({'message': 'Deck removed from DeckBox successfully!'})
