'''Controller for managing Pokemon TCG card operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates

# Local application imports
from init import db
from models.card import Card
from models.cardtype import CardType
from schemas.card_schema import CardSchema

# Blueprint and Schema initialization
card_controller = Blueprint('card_controller', __name__)
card_schema = CardSchema()
cards_schema = CardSchema(many=True)


@validates('name')
def validate_name(self, value):
    """Validate card name length"""
    if len(value) < 1:
        raise ValidationError('Name must not be empty')
    if len(value) > 100:
        raise ValidationError('Name must be less than 100 characters')


@validates('cardtype')
def validate_type(self, value):
    try:
       
        if not isinstance(value, str):
            raise ValidationError('Card type must be text')
        # Get valid Pokemon types from database
        stmt = db.select(Card.cardtype).distinct()
        valid_types = [cardtype.lower() for cardtype in db.session.scalars(stmt).all()]
        if value.lower() not in valid_types:
            raise ValidationError('Invalid Pokemon card type')
    except (ValueError, TypeError):
        raise ValidationError('Invalid card type format')


@validates('cardset_id')
def validate_set_id(self, value):
    """Validate set ID is positive"""
    if value <= 0:
        raise ValidationError('Set ID must be a positive integer')


@card_controller.route('/', methods=['POST'])
def create_card():
    """
    Create a new Pokemon card.
    
    Request Body:
        name (str): Name of the card
        cardtype_id (int): ID of the card type
        cardset_id (int): ID of the set this card belongs to
        
    Returns:
        201: Card created successfully
        400: Missing required fields
        500: Database operation failed
    """
    
    try:
        data = request.json
        if not all(key in data for key in ['name', 'cardtype_id', 'cardset_id']):
            return jsonify({'error': 'Missing required fields'}), 400

        card = Card(
            name=data['name'],
            cardtype_id=data['cardtype_id'],
            cardset_id=data['cardset_id']
        )
        db.session.add(card)
        db.session.commit()
        return card_schema.jsonify(card), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create card', 'details': str(e)}), 500

@card_controller.route('/', methods=['GET'])
def get_all_cards():
    """
    Retrieve all Pokemon cards.
    
    Returns:
        200: List of all cards
        500: Database query failed
    """
    
    try:
        stmt = db.select(Card)
        cards = db.session.scalars(stmt).all()
        return cards_schema.jsonify(cards), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve cards', 'details': str(e)}), 500

@card_controller.route('/<int:card_id>', methods=['GET'])
def get_one_card(card_id):
    """
    Retrieve a specific Pokemon card by ID.
    
    Parameters:
        card_id (int): ID of the card to retrieve
        
    Returns:
        200: Card details
        404: Card not found
        500: Database query failed
    """
    
    try:
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({'error': 'Card not found'}), 404
        return card_schema.jsonify(card), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve card', 'details': str(e)}), 500

@card_controller.route('/<int:card_id>', methods=['PATCH'])
def update_card(card_id):
    """
    Update specific properties of a card.
    
    Parameters:
        card_id (int): ID of the card to update
        
    Request Body:
        name (str, optional): New name for the card
        cardtype (str, optional): New type for the card
        cardset_id (int, optional): New set ID for the card
        
    Returns:
        200: Card updated successfully
        404: Card not found
        500: Database operation failed
    """
    
    try:
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({'error': 'Card not found'}), 404

        data = request.json
        if 'name' in data:
            card.name = data['name']
        if 'cardtype' in data:
            card.cardtype = data['cardtype']
        if 'cardset_id' in data:
            card.cardset_id = data['cardset_id']

        db.session.commit()
        return card_schema.jsonify(card), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Database operation failed',
            'details': str(e)
        }), 500

@card_controller.route('/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """
    Delete a specific Pokemon card.
    
    Parameters:
        card_id (int): ID of the card to delete
        
    Returns:
        200: Card deleted successfully
        404: Card not found
        500: Database operation failed
    """
    
    try:
        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({'error': 'Card not found'}), 404

        db.session.delete(card)
        db.session.commit()
        return jsonify({'message': 'Card deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete card', 'details': str(e)}), 500

@card_controller.route('/filter/by-multiple-types', methods=['GET'])
def filter_by_multiple_types():
    """
    Filter cards by multiple card types.
    
    Query Parameters:
        types (str): Comma-separated list of card types (e.g. fire,water)
        
    Returns:
        200: List of cards matching the specified types
        400: No types provided
        500: Filter operation failed
    """
    
    try:
        if type_names := request.args.get('types'):
            type_list = [type_name.strip().capitalize() for type_name in type_names.split(',')]
            stmt = db.select(Card).join(CardType).filter(CardType.name.in_(type_list))
            cards = db.session.scalars(stmt).all()
            return cards_schema.jsonify(cards), 200
        return jsonify({'error': 'No types provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to filter cards', 'details': str(e)}), 500

@card_controller.route('/filter/by-multiple-sets', methods=['GET'])
def filter_by_multiple_sets():
    """
    Filter cards by multiple set IDs.
    
    Query Parameters:
        sets (str): Comma-separated list of set IDs
        
    Returns:
        200: List of cards from specified sets
        400: No set IDs provided
        500: Filter operation failed
    """
    
    try:
        if set_ids := request.args.get('sets'):
            set_id_list = [int(id) for id in set_ids.split(',')]
            stmt = db.select(Card).filter(Card.cardset_id.in_(set_id_list))
            cards = db.session.scalars(stmt).all()
            return cards_schema.jsonify(cards), 200
        return jsonify({'error': 'No set IDs provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to filter cards', 'details': str(e)}), 500

@card_controller.route('/search', methods=['GET'])
def search_cards():
    """
    Search for Pokemon cards using filters.
    
    Search Parameters:
        name (str, optional): Card name pattern to search for (case insensitive)
        cardtype (str, optional): Card type name pattern to filter by (case insensitive)
        cardset_id (int, optional): Exact set ID to filter by
        
    Returns:
        200: List of matching cards with their relationships
        400: Invalid cardset_id format
        500: Search operation failed
    """    
    try:
        stmt = db.select(Card)
        
        if name := request.args.get('name'):
            stmt = stmt.filter(Card.name.ilike(f'%{name}%'))
        if card_type := request.args.get('cardtype'):
            stmt = stmt.filter(Card.cardtype.has(CardType.name.ilike(f'%{card_type}%')))
        if cardset_id := request.args.get('cardset_id'):
            try:
                cardset_id = int(cardset_id)
                stmt = stmt.filter(Card.cardset_id == cardset_id)
            except ValueError:
                return jsonify({'error': 'Invalid cardset_id format'}), 400
            
        cards = db.session.scalars(stmt).all()
        return cards_schema.jsonify(cards), 200
    
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500