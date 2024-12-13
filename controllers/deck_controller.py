from flask import Blueprint, request, jsonify
from init import db
from models.deck import Deck
from schemas.deck_schema import DeckSchema
from models.card import Card
from schemas.card_schema import CardSchema
from models.deckcard import DeckCard

# Blueprint and Schemas
deck_controller = Blueprint('deck_controller', __name__)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)
card_schema = CardSchema()

# Deck Validation Rules
STANDARD_SETS = {"1", "2", "3", "4", "5"}  # Example Standard-legal sets

# Create a Deck
@deck_controller.route('/decks', methods=['POST'])
def create_deck():
    data = request.json
    deck = Deck(
        name=data['name'],
        description=data.get('description', ''),
        format=data.get('format', 'Standard')  # Default to Standard format
    )
    db.session.add(deck)
    db.session.commit()
    return deck_schema.jsonify(deck), 201

# Read All Decks
@deck_controller.route('/decks', methods=['GET'])
def read_all_decks():
    decks = Deck.query.all()
    return decks_schema.jsonify(decks)

# Read One Deck
@deck_controller.route('/decks/<int:deck_id>', methods=['GET'])
def read_one_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404
    return deck_schema.jsonify(deck)

# Update a Deck
@deck_controller.route('/decks/<int:deck_id>', methods=['PUT'])
def update_deck(deck_id):
    data = request.json
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    deck.name = data.get('name', deck.name)
    deck.description = data.get('description', deck.description)
    deck.format = data.get('format', deck.format)
    db.session.commit()
    return deck_schema.jsonify(deck)

# Delete a Deck
@deck_controller.route('/decks/<int:deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    db.session.delete(deck)
    db.session.commit()
    return jsonify({"message": "Deck deleted successfully!"})

# Add Cards to a Deck
@deck_controller.route('/decks/<int:deck_id>/cards', methods=['POST'])
def add_cards_to_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    data = request.json  # List of {"card_id": x, "quantity": y}
    for card_data in data:
        card_id = card_data.get('card_id')
        quantity = card_data.get('quantity', 1)

        card = Card.query.get(card_id)
        if not card:
            return jsonify({"error": f"Card with ID {card_id} not found"}), 404

        # Add or update DeckCard entry
        deck_card = DeckCard.query.filter_by(deck_id=deck_id, card_id=card_id).first()
        if deck_card:
            deck_card.quantity += quantity  # Increment quantity
        else:
            new_deck_card = DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity)
            db.session.add(new_deck_card)

    db.session.commit()
    return jsonify({"message": "Cards added to deck successfully!"}), 200

# Remove a Card from a Deck
@deck_controller.route('/decks/<int:deck_id>/cards/<int:card_id>', methods=['DELETE'])
def remove_card_from_deck(deck_id, card_id):
    deck_card = DeckCard.query.filter_by(deck_id=deck_id, card_id=card_id).first()
    if not deck_card:
        return jsonify({"error": "Card not found in the deck"}), 404

    db.session.delete(deck_card)
    db.session.commit()
    return jsonify({"message": "Card removed from deck successfully!"}), 200

# Validate a Deck
@deck_controller.route('/decks/<int:deck_id>/validate', methods=['GET'])
def validate_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    errors = []
    total_cards = 0

    # Validation Rules
    for deck_card in deck.cards:  # 'cards' is a relationship in Deck
        card = deck_card.card
        total_cards += deck_card.quantity

        # Rule: No more than 4 copies of a card
        if deck_card.quantity > 4:
            errors.append(f"Card '{card.name}' exceeds the 4-copy limit.")

        # Rule: Validate Standard Format
        if deck.format.lower() == "standard" and card.set_id not in STANDARD_SETS:
            errors.append(f"Card '{card.name}' from set '{card.set_id}' is not Standard legal.")

    # Rule: Deck size must be 60 cards
    if total_cards != 60:
        errors.append("Deck must contain exactly 60 cards.")

    if errors:
        return jsonify({"valid": False, "errors": errors}), 400

    return jsonify({"valid": True, "message": f"Deck is valid for {deck.format} format."}), 200
