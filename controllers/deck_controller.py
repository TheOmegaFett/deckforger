'''Controller for managing Pokemon TCG deck operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
import re

# Local application imports
from init import db
from models.deck import Deck
from models.deckcard import DeckCard
from models.card import Card
from models.cardset import CardSet
from schemas.deck_schema import DeckSchema


deck_controller = Blueprint('deck_controller', __name__)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)


def validate_deck(deck_id, format_id):
    """
    Validate deck composition and format legality.
    
    Parameters:
        deck_id (int): ID of deck to validate
        format_id (int): Format to validate against
        
    Raises:
        ValidationError: If deck violates any format or composition rules
    """
    standard_date = datetime(2022, 7, 1).date()
    expanded_date = datetime(2011, 9, 1).date()

    stmt = (
        db.select(db.func.min(CardSet.release_date))
        .join(Card)
        .join(DeckCard)
        .filter(DeckCard.deck_id == deck_id)
    )
    oldest_card_date = db.session.scalar(stmt)

    if format_id == 1 and oldest_card_date < standard_date:
        raise ValidationError('Deck contains cards not legal in Standard format')
    elif format_id == 2 and oldest_card_date < expanded_date:
        raise ValidationError('Deck contains cards not legal in Expanded format')

    stmt = db.select(DeckCard).filter_by(deck_id=deck_id)
    deck_cards = db.session.scalars(stmt).all()

    card_count = 0
    card_quantities = {}
    basic_energy_pattern = re.compile(r'^Basic \w+ Energy', re.IGNORECASE)

    for deck_card in deck_cards:
        card = db.session.get(Card, deck_card.card_id)
        card_set = db.session.get(CardSet, card.set_id)

        if not card or not card_set:
            raise ValidationError(f'Card or card set not found for deck card ID {deck_card.id}')

        quantity = deck_card.quantity
        card_count += quantity

        if not basic_energy_pattern.match(card.name):
            card_quantities[card.id] = card_quantities.get(card.id, 0) + quantity
            if card_quantities[card.id] > 4:
                raise ValidationError(f'Card \'{card.name}\' has more than 4 copies in the deck.')

    if card_count != 60:
        raise ValidationError(f'Deck must contain exactly 60 cards. Current count: {card_count}')

@deck_controller.route('/', methods=['GET'])
def get_all_decks():
    """
    Retrieve all Pokemon TCG decks.
    
    Returns:
        200: List of all decks
    """
    stmt = db.select(Deck)
    decks = db.session.scalars(stmt).all()
    return decks_schema.jsonify(decks), 200

@deck_controller.route('/', methods=['POST'])
def create_deck():
    """
    Create a new Pokemon TCG deck.
    
    Request Body:
        name (str): Name of the deck
        description (str, optional): Description of the deck
        format_id (int): ID of the format this deck follows
        
    Returns:
        201: Deck created successfully
        400: Validation error in deck composition
    """
    data = request.get_json()
    
    new_deck = Deck(
        name=data['name'],
        description=data.get('description', ''),
        format_id=data['format_id']
    )
    db.session.add(new_deck)
    db.session.commit()

    try:
        validate_deck(new_deck.id, new_deck.format_id)
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return deck_schema.jsonify(new_deck), 201


@deck_controller.route('/<int:deck_id>', methods=['PUT'])
def update_deck(deck_id):
    """
    Update an existing Pokemon TCG deck.
    
    Parameters:
        deck_id (int): ID of the deck to update
        
    Request Body:
        name (str, optional): New name for the deck
        description (str, optional): New description
        format_id (int, optional): New format ID
        
    Returns:
        200: Deck updated successfully
        404: Deck not found
        400: Validation error in deck composition
    """
    deck = db.session.get(Deck, deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    data = request.get_json()
    deck.name = data.get('name', deck.name)
    deck.description = data.get('description', deck.description)
    deck.format_id = data.get('format_id', deck.format_id)

    db.session.commit()

    try:
        validate_deck(deck.id, deck.format_id)
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

    return deck_schema.jsonify(deck), 200


@deck_controller.route('/validate/<int:deck_id>', methods=['GET'])
def validate_deck_rules(deck_id):
    """
    Validate a deck's composition and format legality.
    
    Parameters:
        deck_id (int): ID of the deck to validate
        
    Returns:
        200: Deck is valid with details
        404: Deck not found
        500: Validation check failed
    """
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

