'''Controller for managing Pokemon TCG deck card associations'''


from flask import Blueprint, request, jsonify
from init import db
import re
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
        500: Database operation failed
    """
    try:
        data = request.json
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        if not isinstance(data, list):
            return jsonify({'error': 'Invalid input format. Expected a list of card entries'}), 400

        for item in data:
            card = db.session.get(Card, item['card_id'])
            if not card:
                return jsonify({'error': f'Card with ID {item["card_id"]} not found'}), 404

            quantity = int(item.get('quantity', 1))
            if quantity < 1:
                return jsonify({'error': 'Quantity must be positive'}), 400

            is_basic_energy = BASIC_ENERGY_PATTERN.match(card.name)
            existing_deckcard = db.session.scalar(
                db.select(DeckCard).filter_by(deck_id=deck_id, card_id=item['card_id'])
            )

            if not is_basic_energy and (
                (existing_deckcard and existing_deckcard.quantity + quantity > 4) or
                quantity > 4
            ):
                return jsonify({'error': f'Card {card.name} exceeds 4 copy limit'}), 400

            if existing_deckcard:
                existing_deckcard.quantity += quantity
            else:
                new_deckcard = DeckCard(deck_id=deck_id, card_id=item['card_id'], quantity=quantity)
                db.session.add(new_deckcard)

        db.session.commit()
        return jsonify({'message': 'Cards added successfully'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add cards', 'details': str(e)}), 500

@deckcard_controller.route('/<int:deck_id>/cards', methods=['GET'])
def view_cards_in_deck(deck_id):
    """
    View all cards in a deck.
    
    Parameters:
        deck_id (int): ID of the deck to view cards from
        
    Returns:
        200: List of cards in the deck
        404: Deck not found
        500: Database query failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        stmt = db.select(DeckCard).filter_by(deck_id=deck_id)
        deckcards = db.session.scalars(stmt).all()
        return deckcards_schema.jsonify(deckcards), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve deck cards', 'details': str(e)}), 500

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
        500: Database operation failed
    """
    try:
        deckcard = db.session.scalar(
            db.select(DeckCard).filter_by(deck_id=deck_id, card_id=card_id)
        )
        if not deckcard:
            return jsonify({'error': 'Card not found in deck'}), 404

        db.session.delete(deckcard)
        db.session.commit()
        return jsonify({'message': 'Card removed successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove card', 'details': str(e)}), 500

@deckcard_controller.route('/<int:deck_id>', methods=['PATCH'])
def update_deck_cards(deck_id):
    """
    Update card quantities in a deck with card validation.
    
    Args:
        deck_id (int): ID of the deck to update
        
    Request Body:
        List of objects containing:
            card_id (int): ID of the card
            quantity (int): New quantity for the card
            
    Returns:
        200: Cards updated successfully
        400: Invalid input data or card IDs
        404: Deck not found
        500: Update operation failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        updates = request.json
        if not isinstance(updates, list):
            return jsonify({'error': 'Expected list of card updates'}), 400

        # Validate all card IDs exist before making any changes
        card_ids = [update.get('card_id') for update in updates]
        existing_cards = db.session.scalars(
            db.select(Card).where(Card.id.in_(card_ids))
        ).all()
        existing_card_ids = {card.id for card in existing_cards}
        
        # Check for invalid card IDs
        invalid_cards = set(card_ids) - existing_card_ids
        if invalid_cards:
            return jsonify({
                'error': 'Invalid card IDs',
                'invalid_ids': list(invalid_cards)
            }), 400

        for update in updates:
            card_id = update.get('card_id')
            new_quantity = update.get('quantity')

            if not isinstance(new_quantity, int):
                return jsonify({'error': f'Invalid quantity for card {card_id}'}), 400

            deckcard = db.session.scalar(
                db.select(DeckCard)
                .filter_by(deck_id=deck_id, card_id=card_id)
            )

            if deckcard:
                if new_quantity <= 0:
                    db.session.delete(deckcard)
                else:
                    deckcard.quantity = new_quantity
            elif new_quantity > 0:
                deckcard = DeckCard(
                    deck_id=deck_id,
                    card_id=card_id,
                    quantity=new_quantity
                )
                db.session.add(deckcard)

        db.session.commit()
        return jsonify({'message': 'Deck cards updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Failed to update deck cards',
            'details': str(e)
        }), 500        
        