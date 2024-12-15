'''Controller for managing CLI and database initialization operations'''

# Third-party imports
from datetime import datetime
from flask import Blueprint, jsonify
from flask import current_app

# Local application imports
from init import db
from models import Card, Deck, DeckBox, DeckCard, CardSet
from models.format import Format
from models.cardtype import CardType



cli_controller = Blueprint('cli', __name__)


@cli_controller.route('/run/create', methods=['POST'])
def create_tables():
    """
    Create all database tables.
    
    Returns:
        200: Tables created successfully
    """
    db.create_all()
    return jsonify({'message': 'Tables created successfully!'})


@cli_controller.route('/run/drop', methods=['POST'])
def drop_tables():
    """
    Drop all database tables.
    
    Returns:
        200: Tables dropped successfully
    """
    db.drop_all()
    return jsonify({'message': 'Tables dropped successfully!'})


@cli_controller.route('/run/seed', methods=['POST'])
def seed_tables():
    """
    Seed database with initial data.
    """
    try:
        # Seed Formats
        formats = [
            Format(name='Standard', description='Current sets from Sword & Shield forward'),
            Format(name='Expanded', description='Black & White forward'),
            Format(name='Unlimited', description='All cards from all sets')
        ]
        db.session.add_all(formats)
        db.session.commit()
        
        # Seed Sets
        sets = [
            CardSet(name='Shrouded Fable', release_date='2023-01-01', description='A mysterious set featuring dark creatures'),
            CardSet(name='Eclipse Shadow', release_date='2023-06-01', description='Ghost and psychic focused expansion'),
            CardSet(name='Temporal Forces', release_date='2023-09-15', description='Time-themed Pokemon expansion')
        ]
        db.session.add_all(sets)
        db.session.commit()
        
        # Create the CardType objects
        card_types = [
            CardType(name=type_name) for type_name in [
                'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice',
                'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
                'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy',
                'Supporter', 'Energy'
            ]
        ]
        db.session.add_all(card_types)
        db.session.commit()

        # Create a lookup dictionary for the types
        type_lookup = {
            type_obj.name: type_obj 
            for type_obj in card_types
        }

        # Pokemon cards
        pokemon_cards = [
            Card(name='Fezandipiti EX', cardtype=type_lookup['Dark'], cardset_id=1),
            Card(name='Gengar EX', cardtype=type_lookup['Ghost'], cardset_id=2),
            Card(name='Temporal Tyranitar', cardtype=type_lookup['Dark'], cardset_id=3),
            Card(name='Mewtwo VMAX', cardtype=type_lookup['Psychic'], cardset_id=2),
            Card(name='Darkrai VSTAR', cardtype=type_lookup['Dark'], cardset_id=1),
            Card(name='Zoroark GX', cardtype=type_lookup['Dark'], cardset_id=3),
            Card(name='Lunala V', cardtype=type_lookup['Psychic'], cardset_id=2)
        ]
        
        # Trainer cards
        trainer_cards = [
            Card(name='Dark Patch', cardtype=type_lookup['Supporter'], cardset_id=1),
            Card(name='Time Spiral', cardtype=type_lookup['Supporter'], cardset_id=3),
            Card(name='Fossil Researcher', cardtype=type_lookup['Supporter'], cardset_id=2),
            Card(name='Professor Research', cardtype=type_lookup['Supporter'], cardset_id=1),
            Card(name='Boss Orders', cardtype=type_lookup['Supporter'], cardset_id=2),
            Card(name='Quick Ball', cardtype=type_lookup['Supporter'], cardset_id=3),
            Card(name='Ultra Ball', cardtype=type_lookup['Supporter'], cardset_id=1)
        ]

        # Energy cards
        energy_cards = [
            Card(name='Basic Dark Energy', cardtype=type_lookup['Energy'], cardset_id=1),
            Card(name='Basic Psychic Energy', cardtype=type_lookup['Energy'], cardset_id=1),
            Card(name='Crystal Energy', cardtype=type_lookup['Energy'], cardset_id=2),
            Card(name='Double Dragon Energy', cardtype=type_lookup['Energy'], cardset_id=3),
            Card(name='Horror Energy', cardtype=type_lookup['Energy'], cardset_id=2)
        ]
    
        db.session.add_all(pokemon_cards + trainer_cards + energy_cards)
        db.session.commit()

       

        # Seed DeckBoxes
        deckboxes = [
            DeckBox(name='Competitive Decks', description='Top tier tournament decks'),
            DeckBox(name='Casual Decks', description='Fun and experimental decks'),
            DeckBox(name='Testing Decks', description='Decks in development and testing')
        ]
        db.session.add_all(deckboxes)
        db.session.commit()

        # Seed Decks
        decks = [
            Deck(name='Dark Moon EX', description='A strong dark-themed deck', format_id=1, deckbox_id=1),
            Deck(name='Ghost Control', description='Ghost-type control deck', format_id=2, deckbox_id=1),
            Deck(name='Psychic Control', description='Mewtwo VMAX focused control deck', format_id=1, deckbox_id=1),
            Deck(name='Dark Box', description='Multiple Dark-type attackers', format_id=2, deckbox_id=1),
            Deck(name='Test Dragons', description='Dragon type testing deck', format_id=2, deckbox_id=3)
        ]
        db.session.add_all(decks)
        db.session.commit()

        # DeckCards
        deckcards = [
            DeckCard(deck_id=1, card_id=1, quantity=4),
            DeckCard(deck_id=1, card_id=4, quantity=3),
            DeckCard(deck_id=1, card_id=7, quantity=15),  # Basic Dark Energy
            DeckCard(deck_id=1, card_id=8, quantity=38),  # Basic Psychic Energy
            DeckCard(deck_id=2, card_id=2, quantity=4)
        ]
        db.session.add_all(deckcards)
        db.session.commit()

        # Psychic Control deck (60 cards)
        psychic_control_cards = [
            DeckCard(deck_id=3, card_id=10, quantity=4),  # Mewtwo VMAX
            DeckCard(deck_id=3, card_id=13, quantity=4),  # Professor Research
            DeckCard(deck_id=3, card_id=14, quantity=4),  # Boss Orders
            DeckCard(deck_id=3, card_id=15, quantity=4),  # Quick Ball
            DeckCard(deck_id=3, card_id=16, quantity=4),  # Ultra Ball
            DeckCard(deck_id=3, card_id=8, quantity=40),  # Basic Psychic Energy
        ]

        # Dark Box deck (60 cards)
        dark_box_cards = [
            DeckCard(deck_id=4, card_id=11, quantity=3),  # Darkrai VSTAR
            DeckCard(deck_id=4, card_id=12, quantity=3),  # Zoroark GX
            DeckCard(deck_id=4, card_id=13, quantity=4),  # Professor Research
            DeckCard(deck_id=4, card_id=14, quantity=4),  # Boss Orders
            DeckCard(deck_id=4, card_id=15, quantity=4),  # Quick Ball
            DeckCard(deck_id=4, card_id=18, quantity=2),  # Horror Energy
            DeckCard(deck_id=4, card_id=7, quantity=40),  # Basic Dark Energy
        ]

        # Test Dragons deck (60 cards)
        test_dragons_cards = [
            DeckCard(deck_id=5, card_id=12, quantity=4),  # Zoroark GX
            DeckCard(deck_id=5, card_id=13, quantity=4),  # Professor Research
            DeckCard(deck_id=5, card_id=15, quantity=4),  # Quick Ball
            DeckCard(deck_id=5, card_id=16, quantity=4),  # Ultra Ball
            DeckCard(deck_id=5, card_id=17, quantity=4),  # Double Dragon Energy
            DeckCard(deck_id=5, card_id=7, quantity=20),  # Basic Dark Energy
            DeckCard(deck_id=5, card_id=8, quantity=20),  # Basic Psychic Energy
        ]

        db.session.add_all(psychic_control_cards + dark_box_cards + test_dragons_cards)
        db.session.commit()       
        
        return jsonify({'message': 'Database seeded successfully!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'seeding failed',
            'details': str(e)
        }), 500

@cli_controller.route('/run/cleanup', methods=['POST'])
def cleanup_database():
    """
    Clean up duplicate entries in database.
    
    Removes duplicate:
        - Cards with same name and cardset_id
        - Sets with same name
    
    Returns:
        200: Cleanup completed successfully with count of removed items
        500: Cleanup operation failed
    """
    try:
        # Clean up duplicate cards
        stmt = (
            db.select(Card.name, Card.cardset_id, db.func.count('*'))
            .group_by(Card.name, Card.cardset_id)
            .having(db.func.count('*') > 1)
        )
        duplicate_cards = db.session.execute(stmt).all()
        
        cards_deleted = 0
        for name, cardset_id, count in duplicate_cards:
            stmt = db.select(Card).filter_by(name=name, set_id=cardset_id).offset(1)
            duplicates = db.session.scalars(stmt).all()
            for card in duplicates:
                db.session.delete(card)
                cards_deleted += 1

        # Clean up duplicate sets
        stmt = (
            db.select(CardSet.name, db.func.count('*'))
            .group_by(CardSet.name)
            .having(db.func.count('*') > 1)
        )
        duplicate_sets = db.session.execute(stmt).all()
        
        sets_deleted = 0
        for name, count in duplicate_sets:
            stmt = db.select(CardSet).filter_by(name=name).offset(1)
            duplicates = db.session.scalars(stmt).all()
            for set_ in duplicates:
                db.session.delete(set_)
                sets_deleted += 1

        db.session.commit()

        return jsonify({
            'message': 'Cleanup completed successfully!',
            'cards_removed': cards_deleted,
            'sets_removed': sets_deleted
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Database cleanup failed',
            'details': str(e)
        }), 500


@cli_controller.route('/health')
def health_check():
    """
    Check API health status.
    
    Returns:
        200: API is running
    """
    return jsonify({'status': 'API is running!'}), 200


@cli_controller.route('/routes', methods=['GET'])
def list_routes():
    """
    List all available API routes.
    
    Returns:
        200: List of all registered routes and their methods
    """
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    
    return jsonify({
        'available_routes': routes,
        'total_routes': len(routes)
    }), 200
