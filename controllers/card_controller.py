from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from init import db
from models.card import Card
from schemas.card_schema import CardSchema

# Blueprint and Schema
card_controller = Blueprint('card_controller', __name__)
card_schema = CardSchema()
cards_schema = CardSchema(many=True)

@validates('name')
def validate_name(self, value):
    if len(value) < 1:
        raise ValidationError('Name must not be empty')
    if len(value) > 100:
        raise ValidationError('Name must be less than 100 characters')

@validates('type')
def validate_type(self, value):
    valid_types = ['grass', 'fire', 'water', 'lightning', 'fighting', 'psychic', 'colorless', 'darkness', 'metal', 'dragon', 'fairy']
    if value.lower() not in valid_types:
        raise ValidationError('Invalid Pokemon card type. Must be one of: ' + ', '.join(valid_types))

@validates('set_id')
def validate_set_id(self, value):
    if value <= 0:
        raise ValidationError('Set ID must be a positive integer')

# Create a Card
@card_controller.route('/cards', methods=['POST'])
def create_card():
    data = request.json

    # Validate input
    if not data.get("name") or not data.get("type") or not data.get("set_id"):
        return jsonify({"error": "Name, type, and set_id are required fields."}), 400

    # Create a new card
    card = Card(
        name=data["name"],
        type=data["type"],
        set_id=data["set_id"]
    )
    db.session.add(card)
    db.session.commit()
    return card_schema.jsonify(card), 201

# Read All Cards
@card_controller.route('/', methods=['GET'])
def get_all_cards():
    cards = Card.query.all()
    return cards_schema.jsonify(cards), 200

# Read One Card
@card_controller.route('/<int:card_id>', methods=['GET'])
def get_one_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404
    return card_schema.jsonify(card), 200

# Update a Card
@card_controller.route('/<int:card_id>', methods=['PUT'])
def update_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    data = request.json
    card.name = data.get("name", card.name)
    card.type = data.get("type", card.type)
    card.set_id = data.get("set_id", card.set_id)

    db.session.commit()
    return card_schema.jsonify(card), 200

# Delete a Card
@card_controller.route('/<int:card_id>', methods=['DELETE'])
def delete_card(card_id):
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    db.session.delete(card)
    db.session.commit()
    return jsonify({"message": "Card deleted successfully!"}), 200
