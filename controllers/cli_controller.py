'''Controller for managing CLI and database initialization operations'''

# Third-party imports
from datetime import datetime
from flask import Blueprint, jsonify
from flask import current_app

# Local application imports
from init import db
from models import Card, Deck, DeckBox, DeckCard, CardSet
from models.format import Format


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
    
    Populates the database with:
        - Game formats
        - Card sets
        - Deck boxes
        - Cards
        - Decks
        - Deck-card associations
    
    Returns:
        200: Database seeded successfully
        500: Seeding operation failed
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
            CardSet(name='Temporal Forces', release_date='2023-09-15', description='Time-themed Pokemon expansion'),
            CardSet(name='Crystal Storm', release_date='2023-03-20', description='Featuring powerful crystal-type Pokemon'),
            CardSet(name='Ancient Legends', release_date='2022-11-30', description='Prehistoric and legendary Pokemon')
        ]
        db.session.add_all(sets)
        db.session.commit()

        # Seed DeckBoxes
        deckboxes = [
            DeckBox(name='Competitive Decks', description='Top tier tournament decks'),
            DeckBox(name='Casual Decks', description='Fun and experimental decks'),
            DeckBox(name='Theme Decks', description='Type-focused themed decks'),
            DeckBox(name='Legacy Decks', description='Classic deck builds from past formats')
        ]
        db.session.add_all(deckboxes)
        db.session.commit()

        # Seed Cards
        cards = [
            Card(name='Fezandipiti EX', type='Dark', set_id=1),
            Card(name='Dark Patch', type='Item', set_id=1),
            Card(name='Gengar EX', type='Ghost', set_id=2),
            Card(name='Temporal Tyranitar', type='Dark', set_id=3),
            Card(name='Crystal Charizard', type='Fire', set_id=4),
            Card(name='Ancient Aerodactyl', type='Fighting', set_id=5),
            Card(name='Time Spiral', type='Item', set_id=3),
            Card(name='Crystal Energy', type='Energy', set_id=4),
            Card(name='Fossil Researcher', type='Supporter', set_id=5),
            Card(name='Shadow Rider', type='Ghost', set_id=2)
        ]
        db.session.add_all(cards)
        db.session.commit()

        # Seed Decks
        decks = [
            Deck(name='Dark Moon EX', description='A strong dark-themed deck', format_id=1, deckbox_id=1),
            Deck(name='Ghost Control', description='Ghost-type control deck', format_id=2, deckbox_id=1),
            Deck(name='Crystal Power', description='Crystal-type aggro deck', format_id=1, deckbox_id=1)
        ]
        db.session.add_all(decks)
        db.session.commit()

        # Seed DeckCards
        deckcards = [
            DeckCard(deck_id=1, card_id=1, quantity=4),
            DeckCard(deck_id=1, card_id=2, quantity=3),
            DeckCard(deck_id=2, card_id=3, quantity=4),
            DeckCard(deck_id=3, card_id=5, quantity=3)
        ]
        db.session.add_all(deckcards)
        db.session.commit()

        return jsonify({'message': 'Database seeded successfully!'})

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Seeding failed',
            'details': str(e)
        }), 500


@cli_controller.route('/run/cleanup', methods=['POST'])
def cleanup_database():
    """
    Clean up duplicate entries in database.
    
    Removes duplicate:
        - Cards with same name and set_id
        - Sets with same name
    
    Returns:
        200: Cleanup completed successfully with count of removed items
        500: Cleanup operation failed
    """
    try:
        # Clean up duplicate cards
        stmt = (
            db.select(Card.name, Card.set_id, db.func.count('*'))
            .group_by(Card.name, Card.set_id)
            .having(db.func.count('*') > 1)
        )
        duplicate_cards = db.session.execute(stmt).all()
        
        cards_deleted = 0
        for name, set_id, count in duplicate_cards:
            stmt = db.select(Card).filter_by(name=name, set_id=set_id).offset(1)
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
