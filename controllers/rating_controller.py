'''Controller for managing Pokemon TCG deck rating operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from sqlalchemy import func, and_, true

# Local application imports
from init import db
from models.rating import Rating
from models.deck import Deck
from schemas.rating_schema import RatingSchema

rating_controller = Blueprint('rating_controller', __name__)
rating_schema = RatingSchema()
ratings_schema = RatingSchema(many=True)

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
        500: Database operation failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        data = request.json
        score = int(data.get('score'))
        if not (1 <= score <= 5):
            return jsonify({'error': 'Score must be between 1 and 5'}), 400

        rating = Rating(
            deck_id=deck_id,
            score=score,
            comment=data.get('comment', '')
        )
        db.session.add(rating)
        db.session.commit()
        return rating_schema.jsonify(rating), 201
    except ValueError:
        return jsonify({'error': 'Score must be a number between 1 and 5'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add rating', 'details': str(e)}), 500

@rating_controller.route('/<int:deck_id>/ratings', methods=['GET'])
def get_ratings(deck_id):
    """
    Get all ratings for a deck.
    
    Parameters:
        deck_id (int): ID of the deck to get ratings for
        
    Returns:
        200: List of deck ratings
        404: Deck not found
        500: Database query failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        stmt = db.select(Rating).filter_by(deck_id=deck_id)
        ratings = db.session.scalars(stmt).all()
        return ratings_schema.jsonify(ratings), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve ratings', 'details': str(e)}), 500

@rating_controller.route('/<int:deck_id>/ratings/average', methods=['GET'])
def get_average_rating(deck_id):
    """
    Get average rating for a deck.
    
    Parameters:
        deck_id (int): ID of the deck to get average rating for
        
    Returns:
        200: Average rating value
        404: Deck not found
        500: Calculation failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        stmt = db.select(Rating).filter_by(deck_id=deck_id)
        ratings = db.session.scalars(stmt).all()
        
        if not ratings:
            return jsonify({'average': 0, 'message': 'No ratings yet'})

        average = sum(rating.score for rating in ratings) / len(ratings)
        return jsonify({'average': round(average, 2), 'deck_id': deck_id}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to calculate average', 'details': str(e)}), 500

@rating_controller.route('/decks/top-rated', methods=['GET'])
def get_top_rated_decks():
    """
    Get highest rated decks based on average ratings.
    
    Query Parameters:
        limit (int): Number of decks to return (default 10)
        
    Returns:
        200: List of top rated decks with their average ratings
        500: Query failed
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        stmt = (
            db.select(
                Deck,
                func.avg(Rating.score).label('avg_rating'),
                func.count(Rating.id).label('rating_count')
            )
            .join(Rating)
            .group_by(Deck)
            .order_by(text('avg_rating DESC'))
            .limit(limit)
        )
        
        results = db.session.execute(stmt).all()
        return jsonify([{
            'deck_id': result.Deck.id,
            'name': result.Deck.name,
            'average_rating': float(result.avg_rating),
            'total_ratings': result.rating_count
        } for result in results]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get top rated decks', 'details': str(e)}), 500

@rating_controller.route('/decks/filter/by-rating-range', methods=['GET'])
def filter_decks_by_rating():
    """
    Filter decks by average rating range.
    
    Query Parameters:
        min (float): Minimum average rating
        max (float): Maximum average rating
        
    Returns:
        200: List of decks within specified rating range
        500: Filter operation failed
    """
    try:
        min_rating = request.args.get('min', type=float)
        max_rating = request.args.get('max', type=float)
        
        stmt = (
            db.select(
                Deck,
                func.avg(Rating.score).label('avg_rating')
            )
            .join(Rating)
            .group_by(Deck)
            .having(
                and_(
                    func.avg(Rating.score) >= min_rating if min_rating else true(),
                    func.avg(Rating.score) <= max_rating if max_rating else true()
                )
            )
        )
        
        results = db.session.execute(stmt).all()
        return jsonify([{
            'deck_id': result.Deck.id,
            'name': result.Deck.name,
            'average_rating': float(result.avg_rating)
        } for result in results]), 200
    except Exception as e:
        return jsonify({'error': 'Filter operation failed', 'details': str(e)}), 500