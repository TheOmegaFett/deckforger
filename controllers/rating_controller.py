'''Controller for managing Pokemon TCG deck rating operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates

# Local application imports
from init import db
from models.rating import Rating
from models.deck import Deck
from schemas.rating_schema import RatingSchema


rating_controller = Blueprint('rating_controller', __name__)
rating_schema = RatingSchema()
ratings_schema = RatingSchema(many=True)


@validates('score')
def validate_score(self, value):
    """
    Validate rating score value.
    
    Parameters:
        value (int): Score to validate
        
    Raises:
        ValidationError: If score is not between 1 and 5
    """
    if not 1 <= value <= 5:
        raise ValidationError('Score must be between 1 and 5')


@validates('comment')
def validate_comment(self, value):
    """
    Validate rating comment length.
    
    Parameters:
        value (str): Comment to validate
        
    Raises:
        ValidationError: If comment exceeds maximum length
    """
    if value and len(value) > 500:
        raise ValidationError('Comment must be less than 500 characters')


@rating_controller.route('/<int:deck_id>/ratings', methods=['POST'])
def add_rating(deck_id):
    """
    Add a rating to a deck.
    
    Parameters:
        deck_id (int): ID of the deck to rate
        
    Request Body:
        score (int): Rating score (1-5)
        comment (str, optional): Rating comment
        
    Returns:
        201: Rating added successfully
        400: Invalid score value
        404: Deck not found
    """
    deck = db.session.get(Deck, deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    data = request.json
    try:
        score = int(data.get('score'))
        if not (1 <= score <= 5):
            return jsonify({'error': 'Score must be between 1 and 5'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Score must be a number between 1 and 5'}), 400

    rating = Rating(
        deck_id=deck_id,
        score=score,
        comment=data.get('comment', '')
    )
    db.session.add(rating)
    db.session.commit()
    return rating_schema.jsonify(rating), 201


@rating_controller.route('/<int:deck_id>/ratings', methods=['GET'])
def get_ratings(deck_id):
    """
    Get all ratings for a deck.
    
    Parameters:
        deck_id (int): ID of the deck to get ratings for
        
    Returns:
        200: List of deck ratings
        404: Deck not found
    """
    deck = db.session.get(Deck, deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    stmt = db.select(Rating).filter_by(deck_id=deck_id)
    ratings = db.session.scalars(stmt).all()
    return ratings_schema.jsonify(ratings)


@rating_controller.route('/<int:deck_id>/ratings/average', methods=['GET'])
def get_average_rating(deck_id):
    """
    Get average rating for a deck.
    
    Parameters:
        deck_id (int): ID of the deck to get average rating for
        
    Returns:
        200: Average rating value
        404: Deck not found
    """
    deck = db.session.get(Deck, deck_id)
    if not deck:
        return jsonify({'error': 'Deck not found'}), 404

    stmt = db.select(Rating).filter_by(deck_id=deck_id)
    ratings = db.session.scalars(stmt).all()
    
    if not ratings:
        return jsonify({'average': 0, 'message': 'No ratings yet.'})

    average = sum(rating.score for rating in ratings) / len(ratings)
    return jsonify({'average': round(average, 2), 'deck_id': deck_id})
