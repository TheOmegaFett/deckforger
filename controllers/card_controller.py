'''Controller for managing Pokemon TCG card operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates

# Local application imports
from init import db
from models.card import Card
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
        type (str): Type of the card (grass, fire, water, etc.)
        cardset_id (int): ID of the set this card belongs to
        
    Returns:
        201: Card created successfully
        400: Missing required fields
        409: Card already exists in set
    """
    data = request.json

    if not data.get('name') or not data.get('cardtype') or not data.get('cardset_id'):
        return jsonify({'error': 'Name, cardtype, and cardset_id are required fields.'}), 400

    stmt = db.select(Card).filter_by(name=data['name'], cardset_id=data['cardset_id'])
    existing_card = db.session.scalar(stmt)

    if existing_card:
        return jsonify({'error': f'Card \'{data["name"]}\' already exists in this set'}), 409

    card = Card(
        name=data['name'],
        cardtype=data['cardtype'],
        cardset_id=data['cardset_id']
    )
    db.session.add(card)
    db.session.commit()
    return card_schema.jsonify(card), 201


@card_controller.route('/', methods=['GET'])
def get_all_cards():
    """
    Retrieve all Pokemon cards.
    
    Returns:
        200: List of all cards
    """
    stmt = db.select(Card)
    cards = db.session.scalars(stmt).all()
    return cards_schema.jsonify(cards), 200


@card_controller.route('/<int:card_id>', methods=['GET'])
def get_one_card(card_id):
    """
    Retrieve a specific Pokemon card by ID.
    
    Parameters:
        card_id (int): ID of the card to retrieve
        
    Returns:
        200: Card details
        404: Card not found
    """
    card = db.session.get(Card, card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    return card_schema.jsonify(card), 200


@card_controller.route('/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    """
    Update a specific Pokemon card.
    
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
    card = db.session.get(Card, card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    data = request.json
    card.name = data.get('name', card.name)
    card.cardtype = data.get('cardtype', card.cardtype)
    card.cardset_id = data.get('cardset_id', card.cardset_id)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Database operation failed',
            'details': str(e)
        }), 500
    return card_schema.jsonify(card), 200


@card_controller.route('/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    """
    Delete a specific Pokemon card.
    
    Parameters:
        card_id (int): ID of the card to delete
        
    Returns:
        200: Card deleted successfully
        404: Card not found
    """
    card = db.session.get(Card, card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Card deleted successfully!'}), 200


@card_controller.route('/search', methods=['GET'])
def search_cards():
    """
    Search for Pokemon cards using filters.
    
    Search Parameters:
        name (str, optional): Card name to search for
        type (str, optional): Card type to filter by
        cardset_id (int, optional): Set ID to filter by
        
    Returns:
        200: List of matching cards
    """
    stmt = db.select(Card)
    
    if name := request.args.get('name'):
        stmt = stmt.filter(Card.name.ilike(f'%{name}%'))
    if card_type := request.args.get('cardtype'):
        stmt = stmt.filter(Card.cardtype.ilike(f'%{card_type}%'))
    if cardset_id := request.args.get('cardset_id'):
        stmt = stmt.filter(Card.cardset_id == cardset_id)
        
    cards = db.session.scalars(stmt).all()
    return cards_schema.jsonify(cards), 200

@card_controller.route('/filter/by-multiple-sets', methods=['GET'])
def filter_by_multiple_sets():
    """
    Filter cards by multiple set IDs.
    
    Query Parameters:
        sets (str): Comma-separated list of set IDs
        
    Returns:
        200: List of cards from specified sets
    """
    if set_ids := request.args.get('sets'):
        set_id_list = [int(id) for id in set_ids.split(',')]
        stmt = db.select(Card).filter(Card.cardset_id.in_(set_id_list))
        cards = db.session.scalars(stmt).all()
        return cards_schema.jsonify(cards), 200
    
    return jsonify({'error': 'No set IDs provided'}), 400

@card_controller.route('/filter/by-multiple-types', methods=['GET'])
def filter_by_multiple_types():
    """
    Filter cards by multiple card types.
    
    Query Parameters:
        types (str): Comma-separated list of card types (e.g. fire,water)
        
    Returns:
        200: List of cards matching the specified types
        {
            "cards": [
                {
                    "id": 1,
                    "name": "Charizard",
                    "cardtype": {"name": "Fire"},
                    "cardset": {"name": "Base Set"}
                }
            ]
        }
    """
    if type_names := request.args.get('types'):
        type_list = [type_name.strip().capitalize() for type_name in type_names.split(',')]
        stmt = db.select(Card).join(CardType).filter(CardType.name.in_(type_list))
        cards = db.session.scalars(stmt).all()
        return cards_schema.jsonify(cards), 200
    
    return jsonify({'message': 'Please provide card types to filter by'}), 400
