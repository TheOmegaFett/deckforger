'''Controller for managing Pokemon TCG deck operations'''

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from datetime import datetime
from sqlalchemy import func
import re
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
        422: Deck is invalid with details
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

@deck_controller.route('/import/<deck_name>/<int:format_id>/<int:deckbox_id>', methods=['POST'])
def import_deck(deck_name, format_id, deckbox_id):
    """
    Import a deck from TCG Live format text.
    
    URL Parameters:
        deck_name (str): Name for the imported deck
        format_id (int): Format ID for the deck
        deckbox_id (int): Deck box to store the deck in
        
    Body:
        Raw text in TCG Live format
        
    Returns:
        201: Deck imported successfully
        400: Invalid deck list format
        500: Import operation failed
    """
    try:
        deck_list = request.get_data(as_text=True)
        # Create new deck
        new_deck = Deck(
            name=deck_name,
            description="Imported from TCG Live",
            format_id=format_id,
            deckbox_id=deckbox_id
        )
        db.session.add(new_deck)
        db.session.flush()  # Get deck ID while maintaining transaction
        
        # Parse deck list
        sections = deck_list.split('\n\n')
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            for line in lines[1:]:  # Skip section header
                if not line.strip():
                    continue
                    
        # Parse card line (e.g., "4 Fezandipiti ex SFA 38")
        parts = line.strip().split(' ')
        quantity = int(parts[0])
        set_code = parts[-2]
        card_number = parts[-1]
        # Remove card number and set code, then join remaining parts for name
        name_parts = parts[1:-2]
        # Special handling for card variants
        variants = ['ex', 'VMAX', 'VSTAR', 'V', 'GX']
        card_name = ' '.join(name_parts)
                    
        # Find or create card set
        stmt = db.select(CardSet).filter_by(name=set_code)
        card_set = db.session.scalar(stmt)
        if not card_set:
            card_set = CardSet(
                name=set_code,
                release_date=datetime.now().date(),  # Default to today - fix to actual set date in database cleanup (to be added)
                description=f"Set {set_code}"
                )
            db.session.add(card_set)
            db.session.flush()
                    
            # Find or create card
            stmt = db.select(Card).filter_by(name=card_name, cardset_id=card_set.id)
            card = db.session.scalar(stmt)
            if not card:
                # Determine card type from name/section
                card_type = determine_card_type(card_name, section)
                card = Card(
                    name=card_name,
                    cardtype_id=card_type.id,
                    cardset_id=card_set.id
                )
                db.session.add(card)
                db.session.flush()
                
                # Add card to deck
                deck_card = DeckCard(
                    deck_id=new_deck.id,
                    card_id=card.id,
                    quantity=quantity
                )
                db.session.add(deck_card)

                db.session.commit()
        return jsonify(deck_schema.dump(new_deck)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to import deck', 'details': str(e)}), 500

def determine_card_type(card_name: str, section: str) -> CardType:
    """Helper function to determine and create card type if needed"""
    
    # Map common card indicators to types
    type_indicators = {
        'Stadium': 'Stadium',
        'Item': 'Item',
        'Tool': 'Item',
        'ex': 'Pokemon',
        'V ': 'Pokemon',
        'VMAX': 'Pokemon',
        'VSTAR': 'Pokemon',
        'Basic Energy': 'Energy',
        'Special Energy': 'Energy'
    }
    
    # Determine type from card name and section
    card_type_name = 'Pokemon'  # Default type
    
    if 'Trainer' in section:
        for indicator, type_name in type_indicators.items():
            if indicator in card_name:
                card_type_name = type_name
                break
        if card_name.endswith("'s"):  # Supporter cards typically end with 's
            card_type_name = 'Supporter'
    elif 'Energy' in section:
        card_type_name = 'Energy'
    
    # Find or create the card type
    stmt = db.select(CardType).filter_by(name=card_type_name)
    card_type = db.session.scalar(stmt)
    
    if not card_type:
        card_type = CardType(name=card_type_name)
        db.session.add(card_type)
        db.session.flush()
    
    return card_type

@deck_controller.route('/<int:deck_id>/export', methods=['GET'])
def export_deck(deck_id):
    """
    Export a deck to TCG Live format text.
    
    Parameters:
        deck_id (int): ID of the deck to export
        
    Returns:
        200: Plain text deck list in TCG Live format
        404: Deck not found
        500: Export operation failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        # Group cards by type with correct counting
        pokemon_cards = []
        trainer_cards = []
        energy_cards = []
        
        for deck_card in deck.deck_cards:
            card = deck_card.card
            card_line = f"{deck_card.quantity} {card.name} {card.cardset.name}"
            
            # Ensure energies go in energy section
            if 'Energy' in card.name:
                energy_cards.append(card_line)
            elif card.cardtype.name == 'Pokemon':
                pokemon_cards.append(card_line)
            elif card.cardtype.name in ['Supporter', 'Item', 'Stadium']:
                trainer_cards.append(card_line)

        # Build deck list with correct section counts
        deck_list = [
            f"Pokémon: {len(pokemon_cards)}",
            "",
            *pokemon_cards,
            "",
            f"Trainer: {len(trainer_cards)}",
            "",
            *trainer_cards,
            "",
            f"Energy: {len(energy_cards)}",
            "",
            *energy_cards,
            "",
            f"Total Cards: {sum(dc.quantity for dc in deck.deck_cards)}"
        ]

        return '\n'.join(deck_list), 200, {'Content-Type': 'text/plain'}

    except Exception as e:
        return jsonify({'error': 'Export failed', 'details': str(e)}), 500
        return jsonify({'error': 'Export failed', 'details': str(e)}), 500