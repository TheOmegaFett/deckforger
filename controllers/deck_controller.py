'''Controller for managing Pokemon TCG deck operations'''

# Third-party imports
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import func, and_, true
import re

# Local application imports
from init import db
from models.deck import Deck
from models.deckcard import DeckCard
from models.card import Card
from models.cardset import CardSet
from models.cardtype import CardType
from schemas.deck_schema import DeckSchema

deck_controller = Blueprint('deck_controller', __name__)
deck_schema = DeckSchema()
decks_schema = DeckSchema(many=True)

@deck_controller.route('/', methods=['GET'])
def get_all_decks():
    """
    Retrieve all Pokemon TCG decks.
    
    Returns:
        200: List of all decks
        500: Database query failed
    """
    try:
        stmt = db.select(Deck)
        decks = db.session.scalars(stmt).all()
        return decks_schema.jsonify(decks), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve decks', 'details': str(e)}), 500

@deck_controller.route('/<int:deck_id>', methods=['GET'])
def get_one_deck(deck_id):
    """
    Retrieve a specific deck by ID.
    
    Parameters:
        deck_id (int): ID of the deck to retrieve
        
    Returns:
        200: Deck details
        404: Deck not found
        500: Database query failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404
        return deck_schema.jsonify(deck), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve deck', 'details': str(e)}), 500

@deck_controller.route('/', methods=['POST'])
def create_deck():
    """
    Create a new Pokemon TCG deck.
    
    Request Body:
        name (str): Name of the deck
        description (str, optional): Description of the deck
        format_id (int): ID of the format this deck follows
        deckbox_id (int): ID of the deckbox to contain this deck
        
    Returns:
        201: Deck created successfully
        400: Missing required fields or validation error
        500: Database operation failed
    """
    try:
        data = request.get_json()
        
        required_fields = ['name', 'format_id', 'deckbox_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        new_deck = Deck(
            name=data['name'],
            description=data.get('description', ''),
            format_id=data['format_id'],
            deckbox_id=data['deckbox_id']
        )
        
        db.session.add(new_deck)
        db.session.commit()
        
        return deck_schema.jsonify(new_deck), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create deck', 'details': str(e)}), 500

@deck_controller.route('/<int:deck_id>', methods=['PATCH'])
def update_deck(deck_id):
    """
    Update specific properties of a deck.
    
    Parameters:
        deck_id (int): ID of the deck to update
        
    Request Body:
        name (str, optional): New name for the deck
        description (str, optional): New description
        format_id (int, optional): New format ID
        
    Returns:
        200: Deck updated successfully
        404: Deck not found
        400: Validation error
        500: Database operation failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        data = request.json
        if 'name' in data:
            deck.name = data['name']
        if 'description' in data:
            deck.description = data['description']
        if 'format_id' in data:
            deck.format_id = data['format_id']
            validate_deck(deck.id, deck.format_id)

        db.session.commit()
        return deck_schema.jsonify(deck), 200
    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

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
            
    except ValidationError as e:
        return jsonify({'error': str(e)}), 422
    except Exception as e:
        return jsonify({
            'message': 'Validation check failed',
            'error': str(e),
            'deck_id': deck_id
        }), 500

@deck_controller.route('/search', methods=['GET'])
def search_decks():
    """
    Search and filter decks by format and rating.
    
    Query Parameters:
        format (str): Format name (standard, expanded)
        rating (int): Minimum rating threshold
        
    Returns:
        200: List of matching decks
        500: Search operation failed
    """
    try:
        stmt = db.select(Deck)
        
        if format_name := request.args.get('format'):
            stmt = stmt.filter(Deck.format_id == format_name)
        if rating := request.args.get('rating'):
            stmt = stmt.filter(Deck.rating >= rating)
            
        decks = db.session.scalars(stmt).all()
        return decks_schema.jsonify(decks), 200
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@deck_controller.route('/filter/by-cardtype', methods=['GET'])
def filter_decks_by_cardtype():
    """
    Get decks filtered by card type distribution.
    
    Returns:
        200: Decks with their card type breakdowns
        500: Filter operation failed
    """
    try:
        stmt = db.select(Deck, func.count(CardType.id).label('type_count')).\
               join(DeckCard).join(Card).join(CardType).\
               group_by(Deck.id)
        
        decks = db.session.execute(stmt).all()
        return decks_schema.jsonify(decks), 200
    except Exception as e:
        return jsonify({'error': 'Filter failed', 'details': str(e)}), 500

@deck_controller.route('/top-rated', methods=['GET'])
def get_top_rated_decks():
    """
    Get highest rated decks.
    
    Query Parameters:
        limit (int): Number of decks to return (default 10)
        
    Returns:
        200: List of top rated decks
        500: Query failed
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        stmt = db.select(Deck).\
               order_by(Deck.rating.desc()).\
               limit(limit)
        
        decks = db.session.scalars(stmt).all()
        return decks_schema.jsonify(decks), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get top rated decks', 'details': str(e)}), 500

@deck_controller.route('/filter/by-rating-range', methods=['GET'])
def filter_by_rating():
    """
    Filter decks by rating range.
    
    Query Parameters:
        min (float): Minimum rating
        max (float): Maximum rating
        
    Returns:
        200: List of decks within rating range
        500: Filter operation failed
    """
    try:
        min_rating = request.args.get('min', type=float)
        max_rating = request.args.get('max', type=float)
        
        stmt = db.select(Deck)
        if min_rating:
            stmt = stmt.filter(Deck.rating >= min_rating)
        if max_rating:
            stmt = stmt.filter(Deck.rating <= max_rating)
            
        decks = db.session.scalars(stmt).all()
        return decks_schema.jsonify(decks), 200
    except Exception as e:
        return jsonify({'error': 'Filter failed', 'details': str(e)}), 500

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
    
    if not oldest_card_date:
        raise ValidationError('No cards found in deck')

    # Continue with date comparisons after confirming we have a valid date
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
        card_set = db.session.get(CardSet, card.cardset_id)

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
