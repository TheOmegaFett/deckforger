from datetime import datetime
from flask import jsonify
from flask import Blueprint
from init import db
from models import Card, Deck, DeckBox, DeckCard, CardSet
from models.format import Format

cli_controller = Blueprint("cli", __name__)

@cli_controller.route("/run/create", methods=["POST"])
def create_tables():
    db.create_all()
    return jsonify({"message": "Tables created successfully!"})

@cli_controller.route("/run/seed", methods=["POST"])
def seed_tables():
    # Seed Formats first
    formats = [
        Format(
            name="Standard",
            description="Current sets from Sword & Shield forward"
        ),
        Format(
            name="Expanded",
            description="Black & White forward"
        ),
        Format(
            name="Unlimited",
            description="All cards from all sets"
        )
    ]
    db.session.add_all(formats)
    db.session.commit()
    # Seed Sets
    sets = [
        CardSet(name="Shrouded Fable", release_date="2023-01-01", description="A mysterious set featuring dark creatures"),
        CardSet(name="Eclipse Shadow", release_date="2023-06-01", description="Ghost and psychic focused expansion"),
        CardSet(name="Temporal Forces", release_date="2023-09-15", description="Time-themed Pokemon expansion"),
        CardSet(name="Crystal Storm", release_date="2023-03-20", description="Featuring powerful crystal-type Pokemon"),
        CardSet(name="Ancient Legends", release_date="2022-11-30", description="Prehistoric and legendary Pokemon")
    ]
    db.session.add_all(sets)
    db.session.commit()

    # Seed DeckBoxes
    deckboxes = [
        DeckBox(name="Competitive Decks", description="Top tier tournament decks"),
        DeckBox(name="Casual Decks", description="Fun and experimental decks"),
        DeckBox(name="Theme Decks", description="Type-focused themed decks"),
        DeckBox(name="Legacy Decks", description="Classic deck builds from past formats")
    ]
    db.session.add_all(deckboxes)
    db.session.commit()

    # Seed Decks
    decks = [
        Deck(name="Dark Moon EX", description="A strong dark-themed deck", format_id=1, deckbox_id=1),
        Deck(name="Ghost Control", description="Ghost-type control deck", format_id=2, deckbox_id=1),
        Deck(name="Crystal Power", description="Crystal-type aggro deck", format_id=1, deckbox_id=1),
        Deck(name="Time Loop", description="Temporal Forces combo deck", format_id=1, deckbox_id=2),
        Deck(name="Fossil Revival", description="Ancient Pokemon deck", format_id=2, deckbox_id=2),
        Deck(name="Shadow Riders", description="Ghost-type aggro deck", format_id=1, deckbox_id=3),
        Deck(name="Dark Crystal", description="Dark/Crystal hybrid deck", format_id=1, deckbox_id=3),
        Deck(name="Legacy Legends", description="Classic legendary Pokemon deck", format_id=3, deckbox_id=4)
    ]
    db.session.add_all(decks)
    db.session.commit()

    # Seed Cards with set_id
    cards = [
        Card(name="Fezandipiti EX", type="Dark", set_id=1),
        Card(name="Dark Patch", type="Item", set_id=1),
        Card(name="Gengar EX", type="Ghost", set_id=2),
        Card(name="Temporal Tyranitar", type="Dark", set_id=3),
        Card(name="Crystal Charizard", type="Fire", set_id=4),
        Card(name="Ancient Aerodactyl", type="Fighting", set_id=5),
        Card(name="Time Spiral", type="Item", set_id=3),
        Card(name="Crystal Energy", type="Energy", set_id=4),
        Card(name="Fossil Researcher", type="Supporter", set_id=5),
        Card(name="Shadow Rider", type="Ghost", set_id=2),
        Card(name="Basic Fire Energy", type="Energy", set_id=1),
        Card(name="Basic Water Energy", type="Energy", set_id=1),
        Card(name="Basic Grass Energy", type="Energy", set_id=1),
        Card(name="Basic Lightning Energy", type="Energy", set_id=1),
        Card(name="Basic Psychic Energy", type="Energy", set_id=1),
        Card(name="Basic Fighting Energy", type="Energy", set_id=1),
        Card(name="Basic Darkness Energy", type="Energy", set_id=1),
        Card(name="Basic Metal Energy", type="Energy", set_id=1),
        Card(name="Basic Fairy Energy", type="Energy", set_id=1)
    ]
    db.session.add_all(cards)
    db.session.commit()

    # Seed DeckCards
    deckcards = [
        DeckCard(deck_id=1, card_id=1, quantity=4),
        DeckCard(deck_id=1, card_id=2, quantity=3),
        DeckCard(deck_id=2, card_id=3, quantity=4),
        DeckCard(deck_id=3, card_id=5, quantity=3),
        DeckCard(deck_id=3, card_id=8, quantity=4),
        DeckCard(deck_id=4, card_id=4, quantity=3),
        DeckCard(deck_id=4, card_id=7, quantity=4),
        DeckCard(deck_id=5, card_id=6, quantity=3),
        DeckCard(deck_id=5, card_id=9, quantity=4),
        DeckCard(deck_id=6, card_id=10, quantity=4),
        DeckCard(deck_id=7, card_id=1, quantity=2),
        DeckCard(deck_id=7, card_id=5, quantity=2),
        DeckCard(deck_id=8, card_id=6, quantity=3),
        DeckCard(deck_id=1, card_id=7, quantity=20),  # Darkness Energy for Dark Moon EX
        DeckCard(deck_id=2, card_id=5, quantity=20),  # Psychic Energy for Ghost Control
        DeckCard(deck_id=3, card_id=1, quantity=20),  # Fire Energy for Crystal Power
        DeckCard(deck_id=4, card_id=5, quantity=20),  # Psychic Energy for Time Loop
        DeckCard(deck_id=5, card_id=6, quantity=20),  # Fighting Energy for Fossil Revival
        DeckCard(deck_id=6, card_id=5, quantity=20),  # Psychic Energy for Shadow Riders
        DeckCard(deck_id=7, card_id=7, quantity=20),  # Darkness Energy for Dark Crystal
        DeckCard(deck_id=8, card_id=1, quantity=20)   # Fire Energy for Legacy Legends
    ]
    db.session.add_all(deckcards)
    db.session.commit()

    return jsonify({"message": "Database seeded successfully!"})

@cli_controller.route('/health')
def health_check():
    return jsonify({"status": "API is running!"}), 200

@cli_controller.cli.command("create")
def create_tables():
    with app.app_context():
        db.create_all()
        print("Tables created!")
    
@cli_controller.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@cli_controller.cli.command("seed")
def seed_tables():
    
    # Seed Formats first
    formats = [
        Format(
            name="Standard",
            description="Current sets from Sword & Shield forward"
        ),
        Format(
            name="Expanded",
            description="Black & White forward"
        ),
        Format(
            name="Unlimited",
            description="All cards from all sets"
        )
    ]
    db.session.add_all(formats)
    db.session.commit()
    # Seed Sets
    sets = [
        CardSet(name="Shrouded Fable", release_date="2023-01-01", description="A mysterious set featuring dark creatures"),
        CardSet(name="Eclipse Shadow", release_date="2023-06-01", description="Ghost and psychic focused expansion"),
        CardSet(name="Temporal Forces", release_date="2023-09-15", description="Time-themed Pokemon expansion"),
        CardSet(name="Crystal Storm", release_date="2023-03-20", description="Featuring powerful crystal-type Pokemon"),
        CardSet(name="Ancient Legends", release_date="2022-11-30", description="Prehistoric and legendary Pokemon")
    ]
    db.session.add_all(sets)
    db.session.commit()

    # Seed DeckBoxes
    deckboxes = [
        DeckBox(name="Competitive Decks", description="Top tier tournament decks"),
        DeckBox(name="Casual Decks", description="Fun and experimental decks"),
        DeckBox(name="Theme Decks", description="Type-focused themed decks"),
        DeckBox(name="Legacy Decks", description="Classic deck builds from past formats")
    ]
    db.session.add_all(deckboxes)
    db.session.commit()

    # Seed Decks
    decks = [
        Deck(name="Dark Moon EX", description="A strong dark-themed deck", format_id=1, deckbox_id=1),
        Deck(name="Ghost Control", description="Ghost-type control deck", format_id=2, deckbox_id=1),
        Deck(name="Crystal Power", description="Crystal-type aggro deck", format_id=1, deckbox_id=1),
        Deck(name="Time Loop", description="Temporal Forces combo deck", format_id=1, deckbox_id=2),
        Deck(name="Fossil Revival", description="Ancient Pokemon deck", format_id=2, deckbox_id=2),
        Deck(name="Shadow Riders", description="Ghost-type aggro deck", format_id=1, deckbox_id=3),
        Deck(name="Dark Crystal", description="Dark/Crystal hybrid deck", format_id=1, deckbox_id=3),
        Deck(name="Legacy Legends", description="Classic legendary Pokemon deck", format_id=3, deckbox_id=4)
    ]
    db.session.add_all(decks)
    db.session.commit()

    # Seed Cards with set_id
    cards = [
        Card(name="Fezandipiti EX", type="Dark", set_id=1),
        Card(name="Dark Patch", type="Item", set_id=1),
        Card(name="Gengar EX", type="Ghost", set_id=2),
        Card(name="Temporal Tyranitar", type="Dark", set_id=3),
        Card(name="Crystal Charizard", type="Fire", set_id=4),
        Card(name="Ancient Aerodactyl", type="Fighting", set_id=5),
        Card(name="Time Spiral", type="Item", set_id=3),
        Card(name="Crystal Energy", type="Energy", set_id=4),
        Card(name="Fossil Researcher", type="Supporter", set_id=5),
        Card(name="Shadow Rider", type="Ghost", set_id=2),
        Card(name="Basic Fire Energy", type="Energy", set_id=1),
        Card(name="Basic Water Energy", type="Energy", set_id=1),
        Card(name="Basic Grass Energy", type="Energy", set_id=1),
        Card(name="Basic Lightning Energy", type="Energy", set_id=1),
        Card(name="Basic Psychic Energy", type="Energy", set_id=1),
        Card(name="Basic Fighting Energy", type="Energy", set_id=1),
        Card(name="Basic Darkness Energy", type="Energy", set_id=1),
        Card(name="Basic Metal Energy", type="Energy", set_id=1),
        Card(name="Basic Fairy Energy", type="Energy", set_id=1)
    ]
    db.session.add_all(cards)
    db.session.commit()

    # Seed DeckCards
    deckcards = [
        DeckCard(deck_id=1, card_id=1, quantity=4),
        DeckCard(deck_id=1, card_id=2, quantity=3),
        DeckCard(deck_id=2, card_id=3, quantity=4),
        DeckCard(deck_id=3, card_id=5, quantity=3),
        DeckCard(deck_id=3, card_id=8, quantity=4),
        DeckCard(deck_id=4, card_id=4, quantity=3),
        DeckCard(deck_id=4, card_id=7, quantity=4),
        DeckCard(deck_id=5, card_id=6, quantity=3),
        DeckCard(deck_id=5, card_id=9, quantity=4),
        DeckCard(deck_id=6, card_id=10, quantity=4),
        DeckCard(deck_id=7, card_id=1, quantity=2),
        DeckCard(deck_id=7, card_id=5, quantity=2),
        DeckCard(deck_id=8, card_id=6, quantity=3),
        DeckCard(deck_id=1, card_id=7, quantity=20),  # Darkness Energy for Dark Moon EX
        DeckCard(deck_id=2, card_id=5, quantity=20),  # Psychic Energy for Ghost Control
        DeckCard(deck_id=3, card_id=1, quantity=20),  # Fire Energy for Crystal Power
        DeckCard(deck_id=4, card_id=5, quantity=20),  # Psychic Energy for Time Loop
        DeckCard(deck_id=5, card_id=6, quantity=20),  # Fighting Energy for Fossil Revival
        DeckCard(deck_id=6, card_id=5, quantity=20),  # Psychic Energy for Shadow Riders
        DeckCard(deck_id=7, card_id=7, quantity=20),  # Darkness Energy for Dark Crystal
        DeckCard(deck_id=8, card_id=1, quantity=20)   # Fire Energy for Legacy Legends
    ]
    db.session.add_all(deckcards)
    db.session.commit()
    print("Tables seeded with Sets, DeckBoxes, Decks, Cards, and DeckCard relationships.")

@cli_controller.route("/run/cleanup", methods=["POST"])
def cleanup_database():
    # Clean up duplicate cards
    stmt = (
        db.select(Card.name, Card.set_id, db.func.count('*'))
        .group_by(Card.name, Card.set_id)
        .having(db.func.count('*') > 1)
    )
    duplicate_cards = db.session.execute(stmt).all()
    
    cards_deleted = 0
    for name, set_id, count in duplicate_cards:
        # Keep the first occurrence, delete the rest
        duplicates = Card.query.filter_by(name=name, set_id=set_id).offset(1).all()
        for card in duplicates:
            db.session.delete(card)
            cards_deleted += 1

    # Clean up duplicate sets
    duplicate_sets = db.session.query(CardSet.name, db.func.count('*'))\
        .group_by(CardSet.name)\
        .having(db.func.count('*') > 1)\
        .all()
    
    sets_deleted = 0
    for name, count in duplicate_sets:
        # Keep the first occurrence, delete the rest
        duplicates = CardSet.query.filter_by(name=name).offset(1).all()
        for set_ in duplicates:
            db.session.delete(set_)
            sets_deleted += 1

    # Validate and update deck formats
    decks = Deck.query.all()
    decks_updated = 0
    
    standard_date = datetime(2022, 7, 1)  # Sword & Shield forward
    expanded_date = datetime(2011, 9, 1)  # Black & White forward
    
    for deck in decks:
        oldest_card_date = db.session.query(db.func.min(CardSet.release_date))\
            .join(Card)\
            .join(DeckCard)\
            .filter(DeckCard.deck_id == deck.id)\
            .scalar()
            
        if oldest_card_date >= standard_date:
            deck.format_id = 1  # Standard
        elif oldest_card_date >= expanded_date:
            deck.format_id = 2  # Expanded
        else:
            deck.format_id = 3  # Unlimited
            
        decks_updated += 1
    
    db.session.commit()

    return jsonify({
        "message": "Cleanup and format validation completed successfully!",
        "cards_removed": cards_deleted,
        "sets_removed": sets_deleted,
        "decks_validated": decks_updated
    }), 200

