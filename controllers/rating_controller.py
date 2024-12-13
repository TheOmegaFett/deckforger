from flask import Blueprint, request, jsonify
from init import db
from models.rating import Rating
from models.deck import Deck
from schemas.rating_schema import RatingSchema

rating_controller = Blueprint('rating_controller', __name__)
rating_schema = RatingSchema()
ratings_schema = RatingSchema(many=True)

# Add a Rating to a Deck
@rating_controller.route('/decks/<int:deck_id>/ratings', methods=['POST'])
def add_rating(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    data = request.json
    score = data.get('score')
    if not (1 <= score <= 5):
        return jsonify({"error": "Score must be between 1 and 5"}), 400

    rating = Rating(
        deck_id=deck_id,
        score=score,
        comment=data.get('comment', '')
    )
    db.session.add(rating)
    db.session.commit()
    return rating_schema.jsonify(rating), 201

# Get All Ratings for a Deck
@rating_controller.route('/decks/<int:deck_id>/ratings', methods=['GET'])
def get_ratings(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    return ratings_schema.jsonify(deck.ratings)

# Get Average Rating for a Deck
@rating_controller.route('/decks/<int:deck_id>/ratings/average', methods=['GET'])
def get_average_rating(deck_id):
    deck = Deck.query.get(deck_id)
    if not deck:
        return jsonify({"error": "Deck not found"}), 404

    if not deck.ratings:
        return jsonify({"average": 0, "message": "No ratings yet."})

    average = sum(rating.score for rating in deck.ratings) / len(deck.ratings)
    return jsonify({"average": round(average, 2), "deck_id": deck_id})
