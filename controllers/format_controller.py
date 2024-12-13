from datetime import datetime
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError, validates
from models.card import Card
from models.cardset import CardSet
from models.deckcard import DeckCard
from models.format import Format
from init import db

format_controller = Blueprint('formats', __name__)

@validates('format_id')
def validate_deck_format(self, format_id):
    # Get all cards in the deck through DeckCards
    deck_cards = DeckCard.query.filter_by(deck_id=self.id).all()
    
    # Define format date boundaries
    standard_date = datetime(2022, 7, 1)  # Sword & Shield forward
    expanded_date = datetime(2011, 9, 1)  # Black & White forward
    
    for deck_card in deck_cards:
        card = Card.query.get(deck_card.card_id)
        card_set = CardSet.query.get(card.set_id)
        
        if format_id == 1:  # Standard
            if card_set.release_date < standard_date:
                raise ValidationError(
                    f"Card {card.name} from set {card_set.name} is not legal in Standard format"
                )
        elif format_id == 2:  # Expanded
            if card_set.release_date < expanded_date:
                raise ValidationError(
                    f"Card {card.name} from set {card_set.name} is not legal in Expanded format"
                )
        # Format 3 is Unlimited, all cards allowed


@format_controller.route('/formats', methods=['GET'])
def get_formats():
    formats = Format.query.all()
    return jsonify([format.to_dict() for format in formats])

@format_controller.route('/formats/<int:format_id>', methods=['GET'])
def get_format(format_id):
    format = Format.query.get_or_404(format_id)
    return jsonify(format.to_dict())

@format_controller.route('/formats', methods=['POST'])
def create_format():
    data = request.get_json()
    
    # Validation
    required_fields = ['name', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check for duplicate format names
    if Format.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Format name already exists'}), 409

    new_format = Format(
        name=data['name'],
        description=data['description']
    )
    
    db.session.add(new_format)
    db.session.commit()
    
    return jsonify(new_format.to_dict()), 201

@format_controller.route('/formats/<int:format_id>', methods=['PUT'])
def update_format(format_id):
    format = Format.query.get_or_404(format_id)
    data = request.get_json()
    
    if 'name' in data:
        existing_format = Format.query.filter_by(name=data['name']).first()
        if existing_format and existing_format.id != format_id:
            return jsonify({'error': 'Format name already exists'}), 409
    
    # Update fields
    for field in ['name', 'description']:
        if field in data:
            setattr(format, field, data[field])
    
    db.session.commit()
    return jsonify(format.to_dict())

@format_controller.route('/formats/<int:format_id>', methods=['DELETE'])
def delete_format(format_id):
    format = Format.query.get_or_404(format_id)
    db.session.delete(format)
    db.session.commit()
    return jsonify({'message': 'Format deleted successfully'}), 200

