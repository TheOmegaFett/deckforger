from flask import Blueprint, request, jsonify
from init import db
from models.deck import Deck
from models.deckcard import DeckCard
from models.card import Card
from models.cardset import CardSet
from schemas.deck_schema import DeckSchema
from marshmallow import ValidationError
from datetime import datetime
import re

deck_controller = Blueprint('deck_controller', __name__)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)

def validate_deck(deck_id, format_id):
    # Convert datetime boundaries to date objects
    standard_date = datetime(2022, 7, 1).date()
    expanded_date = datetime(2011, 9, 1).date()

    # Get release date using modern query syntax
    stmt = (
        db.select(db.func.min(CardSet.release_date))
        .join(Card)
        .join(DeckCard)
        .filter(DeckCard.deck_id == deck_id)
    )
    oldest_card_date = db.session.scalar(stmt)

    # Format validation using oldest card date
    if format_id == 1 and oldest_card_date < standard_date:
        raise ValidationError('Deck contains cards not legal in Standard format')
    elif format_id == 2 and oldest_card_date < expanded_date:
        raise ValidationError('Deck contains cards not legal in Expanded format')

    # Continue with card count and quantity validation
    deck_cards = db.session.scalars(
        db.select(DeckCard).filter_by(deck_id=deck_id)
    ).all()

    card_count = 0
    card_quantities = {}

    # Regex pattern for Basic Energy cards (e.g., 'Basic Fire Energy', 'Basic Water Energy')
    basic_energy_pattern = re.compile(r'^Basic \w+ Energy', re.IGNORECASE)
    for deck_card in deck_cards:
        card = Card.query.get(deck_card.card_id)
        card_set = CardSet.query.get(card.set_id)

        if not card or not card_set:
            raise ValidationError(f'Card or card set not found for deck card ID {deck_card.id}')

        # Increment card count
        quantity = deck_card.quantity
        card_count += quantity

        # Check for Basic Energy cards using regex
        if not basic_energy_pattern.match(card.name):
            # Track card quantities for non-Basic Energy cards
            card_quantities[card.id] = card_quantities.get(card.id, 0) + quantity
            if card_quantities[card.id] > 4:
                raise ValidationError(f'Card \'{card.name}\' has more than 4 copies in the deck.')

    # Enforce 60 card deck rule
    if card_count != 60:
        raise ValidationError(f'Deck must contain exactly 60 cards. Current count: {card_count}')

# Create a Deck
@deck_controller.route('/', methods=['POST'])
def create_deck():
    data = request.get_json()
    
    # Create a new Deck
    new_deck = Deck(
        name=data['name'],
        description=data.get('description', ''),
        format_id=data['format_id']
    )
    db.session.add(new_deck)
    db.session.commit()

    # Validate deck rules
    try:
        validate_deck(new_deck.id, new_deck.format_id)
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return deck_schema.jsonify(new_deck), 201

# Update a Deck
@deck_controller.route('/<int:deck_id>', methods=['PUT'])
def update_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    data = request.get_json()
    deck.name = data.get('name', deck.name)
    deck.description = data.get('description', deck.description)
    deck.format_id = data.get('format_id', deck.format_id)

    db.session.commit()

    # Validate deck rules
    try:
        validate_deck(deck.id, deck.format_id)
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return deck_schema.jsonify(deck), 200

@deck_controller.route('/validate/<int:deck_id>', methods=['GET'])
def validate_deck_rules(deck_id):
    try:
        stmt = db.select(Deck).filter_by(id=deck_id)
        deck = db.session.scalar(stmt)
        
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
            
        validate_deck(deck.id, deck.format_id)
        
        return jsonify({
            'message': 'Deck is valid!',
            'deck_name': deck.name,
            'format': deck.format_id,
            'card_count': sum(dc.quantity for dc in deck.deck_cards)
        }), 200
            
    except Exception as e:
        return jsonify({
            'message': 'Validation check failed',
            'error': str(e),
            'deck_id': deck_id
        }), 500
