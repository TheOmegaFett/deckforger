from flask import Blueprint, request, jsonify
from init import db
from models.deckbox import DeckBox
from schemas.deckbox_schema import DeckBoxSchema
from models.deck import Deck
from schemas.deck_schema import DeckSchema

# Blueprint and Schema Setup
deckbox_controller = Blueprint('deckbox_controller', __name__)
deckbox_schema = DeckBoxSchema()
deckboxes_schema = DeckBoxSchema(many=True)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)

# Create a DeckBox
@deckbox_controller.route('/deckboxes', methods=['POST'])
def create_deckbox():
    data = request.json
    deckbox = DeckBox(
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(deckbox)
    db.session.commit()
    return deckbox_schema.jsonify(deckbox), 201

# Read All DeckBoxes
@deckbox_controller.route('/deckboxes', methods=['GET'])
def read_all_deckboxes():
    deckboxes = DeckBox.query.all()
    return deckboxes_schema.jsonify(deckboxes)

# Read One DeckBox
@deckbox_controller.route('/deckboxes/<int:deckbox_id>', methods=['GET'])
def read_one_deckbox(deckbox_id):
    deckbox = DeckBox.query.get(deckbox_id)
    if not deckbox:
        return jsonify({"error": "DeckBox not found"}), 404
    return deckbox_schema.jsonify(deckbox)

# Update a DeckBox
@deckbox_controller.route('/deckboxes/<int:deckbox_id>', methods=['PUT'])
def update_deckbox(deckbox_id):
    data = request.json
    deckbox = DeckBox.query.get(deckbox_id)
    if not deckbox:
        return jsonify({"error": "DeckBox not found"}), 404

    deckbox.name = data.get('name', deckbox.name)
    deckbox.description = data.get('description', deckbox.description)
    db.session.commit()
    return deckbox_schema.jsonify(deckbox)

# Delete a DeckBox
@deckbox_controller.route('/deckboxes/<int:deckbox_id>', methods=['DELETE'])
def delete_deckbox(deckbox_id):
    deckbox = DeckBox.query.get(deckbox_id)
    if not deckbox:
        return jsonify({"error": "DeckBox not found"}), 404

    db.session.delete(deckbox)
    db.session.commit()
    return jsonify({"message": "DeckBox deleted successfully!"})

# Show all Decks in a DeckBox
@deckbox_controller.route('/deckboxes/<int:deckbox_id>/decks', methods=['GET'])
def show_decks_in_deckbox(deckbox_id):
    deckbox = DeckBox.query.get(deckbox_id)
    if not deckbox:
        return jsonify({"error": "DeckBox not found"}), 404

    return decks_schema.jsonify(deckbox.decks)

# Add a Deck to a DeckBox
@deckbox_controller.route('/deckboxes/<int:deckbox_id>/decks', methods=['POST'])
def add_deck_to_deckbox(deckbox_id):
    data = request.json

    # Validate DeckBox exists
    deckbox = DeckBox.query.get(deckbox_id)
    if not deckbox:
        return jsonify({"error": "DeckBox not found"}), 404

    # Create a new Deck and associate it with this DeckBox
    deck = Deck(
        name=data['name'],
        description=data.get('description', ''),
        format=data.get('format', 'Standard'),
        deckbox_id=deckbox_id
    )
    db.session.add(deck)
    db.session.commit()

    return deck_schema.jsonify(deck), 201

# Remove a Deck from a DeckBox
@deckbox_controller.route('/deckboxes/<int:deckbox_id>/decks/<int:deck_id>', methods=['DELETE'])
def remove_deck_from_deckbox(deckbox_id, deck_id):
    # Validate DeckBox exists
    deckbox = DeckBox.query.get(deckbox_id)
    if not deckbox:
        return jsonify({"error": "DeckBox not found"}), 404

    # Validate Deck exists and belongs to this DeckBox
    deck = Deck.query.filter_by(id=deck_id, deckbox_id=deckbox_id).first()
    if not deck:
        return jsonify({"error": "Deck not found in this DeckBox"}), 404

    db.session.delete(deck)
    db.session.commit()
    return jsonify({"message": "Deck removed from DeckBox successfully!"})
