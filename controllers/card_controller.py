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


@validates('type')
def validate_type(self, value):
    """Validate card type against allowed types"""
    valid_types = ['grass', 'fire', 'water', 'lightning', 'fighting', 
                   'psychic', 'colorless', 'darkness', 'metal', 'dragon', 'fairy']
    if value.lower() not in valid_types:
        raise ValidationError('Invalid Pokemon card type. Must be one of: ' + ', '.join(valid_types))


@validates('set_id')
def validate_set_id(self, value):
    """Validate set ID is positive"""
    if value <= 0:
        raise ValidationError('Set ID must be a positive integer')


@card_controller.route('/', methods=['POST'])
def create_card():
    """Create a new card"""
    data = request.json

    if not data.get('name') or not data.get('type') or not data.get('set_id'):
        return jsonify({'error': 'Name, type, and set_id are required fields.'}), 400

    existing_card = Card.query.filter_by(
        name=data['name'],
        set_id=data['set_id']
    ).first()

    if existing_card:
        return jsonify({'error': f'Card \'{data["name"]}\' already exists in this set'}), 409

    card = Card(
        name=data['name'],
        type=data['type'],
        set_id=data['set_id']
    )
    db.session.add(card)
    db.session.commit()
    return card_schema.jsonify(card), 201


@card_controller.route('/', methods=['GET'])
def get_all_cards():
    """Retrieve all cards"""
    cards = Card.query.all()
    return cards_schema.jsonify(cards), 200


@card_controller.route('/<int:card_id>', methods=['GET'])
def get_one_card(card_id):
    """Retrieve a specific card by ID"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404
    return card_schema.jsonify(card), 200


@card_controller.route('/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    """Update a specific card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    data = request.json
    card.name = data.get('name', card.name)
    card.type = data.get('type', card.type)
    card.set_id = data.get('set_id', card.set_id)

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
    """Delete a specific card"""
    card = Card.query.get(card_id)
    if not card:
        return jsonify({'error': 'Card not found'}), 404

    db.session.delete(card)
    db.session.commit()
    return jsonify({'message': 'Card deleted successfully!'}), 200


@card_controller.route('/search', methods=['GET'])
def search_cards():
    """Search cards by name, type, and set_id"""
    name = request.args.get('name', '')
    card_type = request.args.get('type', '')
    set_id = request.args.get('set_id')
    
    stmt = db.select(Card)
    
    if name:
        stmt = stmt.filter(Card.name.ilike(f'%{name}%'))
    if card_type:
        stmt = stmt.filter(Card.type.ilike(f'%{card_type}%'))
    if set_id:
        stmt = stmt.filter(Card.set_id == set_id)
        
    cards = db.session.scalars(stmt).all()
    return cards_schema.jsonify(cards), 200
