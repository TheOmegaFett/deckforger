from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from init import db
from models.deckcard import DeckCard
from schemas.deckcard_schema import DeckCardSchema
from models.deck import Deck
from models.card import Card

# Blueprint and Schema
deckcard_controller = Blueprint("deckcard_controller", __name__)
deckcard_schema = DeckCardSchema()
deckcards_schema = DeckCardSchema(many=True)

@validates('quantity')
def validate_quantity(self, value):
    if value < 1:
        raise ValidationError('Quantity must be at least 1')
    if value > 4:
        raise ValidationError('Maximum 4 copies of a card allowed per deck')


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

        # Create or update the DeckCard entry
        deckcard = DeckCard.query.filter_by(deck_id=deck_id, card_id=card_id).first()
        if deckcard:
            deckcard.quantity += quantity
        else:
            deckcard = DeckCard(deck_id=deck_id, card_id=card_id, quantity=quantity)
            db.session.add(deckcard)

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
