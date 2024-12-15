'''Controller for managing Pokemon TCG deck card associations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from init import db
import re

# Local application imports
from models.deckcard import DeckCard
from schemas.deckcard_schema import DeckCardSchema
from models.deck import Deck
from models.card import Card


# Blueprint and Schema Setup
deckcard_controller = Blueprint('deckcard_controller', __name__)
deckcard_schema = DeckCardSchema()
deckcards_schema = DeckCardSchema(many=True)

# Constants
BASIC_ENERGY_PATTERN = re.compile(r'^Basic \w+ Energy', re.IGNORECASE)


@deckcard_controller.route('/<int:deck_id>/cards', methods=['POST'])
def add_cards_to_deck(deck_id):
    """
    Add cards to a deck.
    
    Parameters:
        deck_id (int): ID of the deck to add cards to
        
    Request Body:
        list of objects containing:
            card_id (int): ID of the card to add
            quantity (int): Number of copies to add
            
    Returns:
        201: Cards added successfully
        400: Invalid input format or quantity
        404: Deck or card not found
    """
    data = request.json

    deck = db.session.get(Deck, deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    if not isinstance(data, list) or not all('card_id' in item and 'quantity' in item for item in data):
        return jsonify({'error': 'Invalid input format. Expected a list of {card_id, quantity}'}), 400

    for item in data:
        card_id = item['card_id']
        quantity = item.get('quantity', 1)

        card = db.session.get(Card, card_id)
        if not card:
            return jsonify({'error': f'Card with ID {card_id} not found'}), 404
        try:
            quantity = int(item.get('quantity', 1))
            if quantity < 1:
                return jsonify({'error': 'Quantity must be a positive number'}), 400
        except (ValueError, TypeError):
                  return jsonify({'error': 'Quantity must be a valid number'}), 400
        is_basic_energy = BASIC_ENERGY_PATTERN.match(card.name)
        stmt = db.select(DeckCard).filter_by(deck_id=deck_id, card_id=card_id)
        existing_deckcard = db.session.scalar(stmt)
        current_quantity = existing_deckcard.quantity if existing_deckcard else 0

        if not is_basic_energy and (current_quantity + quantity) > 4:
            return jsonify({
                'error': f'Card \'{card.name}\' exceeds the maximum of 4 copies allowed in the deck.'
            }), 400

        if existing_deckcard:
            existing_deckcard.quantity += quantity
        else:
            new_deckcard = DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity)
            db.session.add(new_deckcard)

    db.session.commit()
    return jsonify({'message': 'Cards added successfully!'}), 201


@deckcard_controller.route('/<int:deck_id>/cards', methods=['GET'])
def view_cards_in_deck(deck_id):
    """
    View all cards in a deck.
    
    Parameters:
        deck_id (int): ID of the deck to view cards from
        
    Returns:
        200: List of cards in the deck
        404: Deck not found
    """
    deck = db.session.get(Deck, deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    stmt = db.select(DeckCard).filter_by(deck_id=deck_id)
    deckcards = db.session.scalars(stmt).all()
    return deckcards_schema.jsonify(deckcards), 200


@deckcard_controller.route('/<int:deck_id>/cards/<int:card_id>', methods=['DELETE'])
def remove_card_from_deck(deck_id, card_id):
    """
    Remove a card from a deck.
    
    Parameters:
        deck_id (int): ID of the deck containing the card
        card_id (int): ID of the card to remove
        
    Returns:
        200: Card removed successfully
        404: Card not found in deck
    """
    stmt = db.select(DeckCard).filter_by(deck_id=deck_id, card_id=card_id)
    deckcard = db.session.scalar(stmt)
    if not deckcard:
        return jsonify({'error': 'Card not found in the deck'}), 404

    db.session.delete(deckcard)
    db.session.commit()
    return jsonify({'message': 'Card removed from deck successfully!'}), 200


@deckcard_controller.route('/<int:deck_id>', methods=['PUT'])
def update_deck_cards(deck_id):
    """
    Update all cards in a deck.
    
    Parameters:
        deck_id (int): ID of the deck to update
        
    Request Body:
        cards: List of objects containing card_id and quantity
        
    Returns:
        200: Deck cards updated successfully
    """
    data = request.get_json()
    
    stmt = db.select(DeckCard).filter_by(deck_id=deck_id)
    db.session.scalars(stmt).all().delete()
    
    for card_data in data['cards']:
        new_deckcard = DeckCard(
            deck_id=deck_id,
            card_id=card_data['card_id'],
            quantity=card_data['quantity']
        )
        db.session.add(new_deckcard)
    
    db.session.commit()
    
    return jsonify({'message': 'Deck cards updated successfully!'}), 200