from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from init import db, app
from models.deckcard import DeckCard
from schemas.deckcard_schema import DeckCardSchema
from models.deck import Deck
from models.card import Card
import re

# Blueprint and Schema
deckcard_controller = Blueprint("deckcard_controller", __name__)
deckcard_schema = DeckCardSchema()
deckcards_schema = DeckCardSchema(many=True)

# Regex pattern to match Basic {Type} Energy cards
BASIC_ENERGY_PATTERN = re.compile(r"^Basic \w+ Energy$", re.IGNORECASE)

# Add Cards to a Deck
@deckcard_controller.route("/<int:deck_id>/cards", methods=["POST"])
def add_cards_to_deck(deck_id):
    data = request.json

    # Check if the deck exists
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    # Validate input (expect a list of card_id and quantity)
    if not isinstance(data, list) or not all("card_id" in item and "quantity" in item for item in data):
        return jsonify({"error": "Invalid input format. Expected a list of {card_id, quantity}"}), 400

    # Process each card
    for item in data:
        card_id = item["card_id"]
        quantity = item.get("quantity", 1)  # Default to 1 if not provided

        # Check if the card exists
        card = Card.query.get(card_id)
        if not card:
            return jsonify({"error": f"Card with ID {card_id} not found"}), 404

        # Quantity Validation
        if quantity < 1:
            return jsonify({"error": "Quantity must be at least 1"}), 400

        # Check if the card is a Basic Energy
        is_basic_energy = BASIC_ENERGY_PATTERN.match(card.name)

        # Count total copies of the card in the deck
        existing_deckcard = DeckCard.query.filter_by(deck_id=deck_id, card_id=card_id).first()
        current_quantity = existing_deckcard.quantity if existing_deckcard else 0

        if not is_basic_energy and (current_quantity + quantity) > 4:
            return jsonify({
                "error": f"Card '{card.name}' exceeds the maximum of 4 copies allowed in the deck."
            }), 400

        # Add or update the DeckCard entry
        if existing_deckcard:
            existing_deckcard.quantity += quantity
        else:
            new_deckcard = DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity)
            db.session.add(new_deckcard)

    db.session.commit()
    return jsonify({"message": "Cards added successfully!"}), 201

# View All Cards in a Deck
@deckcard_controller.route("/<int:deck_id>/cards", methods=["GET"])
def view_cards_in_deck(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    deckcards = DeckCard.query.filter_by(deck_id=deck_id).all()
    return deckcards_schema.jsonify(deckcards), 200

# Remove a Card from a Deck
@deckcard_controller.route("/<int:deck_id>/cards/<int:card_id>", methods=["DELETE"])
def remove_card_from_deck(deck_id, card_id):
    # Find the DeckCard entry
    deckcard = DeckCard.query.filter_by(deck_id=deck_id, card_id=card_id).first()
    if not deckcard:
        return jsonify({"error": "Card not found in the deck"}), 404

    db.session.delete(deckcard)
    db.session.commit()
    return jsonify({"message": "Card removed from deck successfully!"}), 200
