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
        500: Database operation failed
    """
    try:
        data = request.json
        deckbox = DeckBox(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(deckbox)
        db.session.commit()
        return deckbox_schema.jsonify(deckbox), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create deckbox', 'details': str(e)}), 500

@deckbox_controller.route('/', methods=['GET'])
def read_all_deckboxes():
    """
    Retrieve all deck boxes.
    
    Returns:
        200: List of all deck boxes
        500: Database query failed
    """
    try:
        stmt = db.select(DeckBox)
        deckboxes = db.session.scalars(stmt).all()
        return deckboxes_schema.jsonify(deckboxes), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve deckboxes', 'details': str(e)}), 500

@deckbox_controller.route('/<int:deckbox_id>', methods=['GET'])
def read_one_deckbox(deckbox_id):
    """
    Retrieve a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to retrieve
        
    Returns:
        200: Deck box details
        404: Deck box not found
        500: Database query failed
    """
    try:
        deckbox = db.session.get(DeckBox, deckbox_id)
        if not deckbox:
            return jsonify({'error': 'DeckBox not found'}), 404
        return deckbox_schema.jsonify(deckbox), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve deckbox', 'details': str(e)}), 500

@deckbox_controller.route('/<int:deckbox_id>', methods=['PATCH'])
def update_deckbox(deckbox_id):
    """
    Update specific properties of a deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to update
        
    Request Body:
        name (str, optional): New name for the deck box
        description (str, optional): New description
        
    Returns:
        200: Deck box updated successfully
        404: Deck box not found
        500: Database operation failed
    """
    try:
        deckbox = db.session.get(DeckBox, deckbox_id)
        if not deckbox:
            return jsonify({'error': 'DeckBox not found'}), 404

        data = request.json
        if 'name' in data:
            deckbox.name = data['name']
        if 'description' in data:
            deckbox.description = data['description']

        db.session.commit()
        return deckbox_schema.jsonify(deckbox), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update deckbox', 'details': str(e)}), 500

@deckbox_controller.route('/<int:deckbox_id>', methods=['DELETE'])
def delete_deckbox(deckbox_id):
    """
    Delete a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to delete
        
    Returns:
        200: Deck box deleted successfully
        404: Deck box not found
        500: Database operation failed
    """
    try:
        deckbox = db.session.get(DeckBox, deckbox_id)
        if not deckbox:
            return jsonify({'error': 'DeckBox not found'}), 404

        db.session.delete(deckbox)
        db.session.commit()
        return jsonify({'message': 'DeckBox deleted successfully!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete deckbox', 'details': str(e)}), 500

@deckbox_controller.route('/<int:deckbox_id>/decks', methods=['GET'])
def show_decks_in_deckbox(deckbox_id):
    """
    List all decks in a specific deck box.
    
    Parameters:
        deckbox_id (int): ID of the deck box to list decks from
        
    Returns:
        200: List of decks in the deck box
        404: Deck box not found
        500: Database query failed
    """
    try:
        deckbox = db.session.get(DeckBox, deckbox_id)
        if not deckbox:
            return jsonify({'error': 'DeckBox not found'}), 404
        return decks_schema.jsonify(deckbox.decks), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve decks', 'details': str(e)}), 500

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
        500: Database operation failed
    """
    try:
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
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add deck', 'details': str(e)}), 500

@deckbox_controller.route('/search', methods=['GET'])
def search_deckboxes():
    """
    Search deckboxes by name.
    
    Query Parameters:
        name (str): Name to search for
        
    Returns:
        200: List of matching deckboxes
        500: Search operation failed
    """
    try:
        stmt = db.select(DeckBox)
        if name := request.args.get('name'):
            stmt = stmt.filter(DeckBox.name.ilike(f'%{name}%'))
        deckboxes = db.session.scalars(stmt).all()
        return deckboxes_schema.jsonify(deckboxes), 200
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@deckbox_controller.route('/<int:deckbox_id>/decks/filter', methods=['GET'])
def filter_deckbox_decks(deckbox_id):
    """
    Filter decks within a specific deckbox.
    
    Parameters:
        deckbox_id (int): ID of the deckbox to filter decks from
        
    Query Parameters:
        format (str): Filter by deck format
        name (str): Filter by deck name
        
    Returns:
        200: Filtered list of decks
        404: Deckbox not found
        500: Filter operation failed
    """
    try:
        deckbox = db.session.get(DeckBox, deckbox_id)
        if not deckbox:
            return jsonify({'error': 'Deckbox not found'}), 404

        stmt = db.select(Deck).filter(Deck.deckbox_id == deckbox_id)
        
        if format_name := request.args.get('format'):
            stmt = stmt.filter(Deck.format.ilike(f'%{format_name}%'))
        if deck_name := request.args.get('name'):
            stmt = stmt.filter(Deck.name.ilike(f'%{deck_name}%'))
            
        decks = db.session.scalars(stmt).all()
        return decks_schema.jsonify(decks), 200
    except Exception as e:
        return jsonify({'error': 'Filter failed', 'details': str(e)}), 500