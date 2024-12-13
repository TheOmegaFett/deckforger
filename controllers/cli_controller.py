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
     # Seed Sets first
    sets = [
        CardSet(
            name="Shrouded Fable",
            release_date="2023-01-01",
            description="A mysterious set featuring dark creatures"
        ),
        CardSet(
            name="Eclipse Shadow",
            release_date="2023-06-01",
            description="Ghost and psychic focused expansion"
        )
    ]
    db.session.add_all(sets)
    db.session.commit()
    
    
    deckbox = DeckBox(name="Competitive Decks", description="Top tier decks.")
    db.session.add(deckbox)
    db.session.commit()

    card = Card(name="Fezandipiti EX", type="Dark", set_id=1)
    db.session.add(card)
    db.session.commit()

    decks = [
        Deck(
            name="Dark Moon EX",
            description="A strong dark-themed deck.",
            format_id=formats[0].id,  # Standard
            deckbox_id=deckbox.id
        ),
        Deck(
            name="Ghost Control",
            description="A ghost-themed deck for control strategies.",
            format_id=formats[1].id,  # Expanded
            deckbox_id=deckbox.id
        ),
        Deck(
            name="Fun Energy Deck",
            description="A casual deck with quirky combos.",
            format_id=formats[2].id,  # Unlimited
            deckbox_id=deckbox.id
        )
    ]
    db.session.add_all(decks)
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
    with app.app_context():
        # Seed Sets first
        sets = [
            CardSet(
                name="Shrouded Fable",
                release_date="2023-01-01",
                description="A mysterious set featuring dark creatures"
            ),
            CardSet(
                name="Eclipse Shadow",
                release_date="2023-06-01",
                description="Ghost and psychic focused expansion"
            )
        ]
        db.session.add_all(sets)
        db.session.commit()

        # Seed DeckBoxes
        deckboxes = [
            DeckBox(
                name="Competitive Decks",
                description="A collection of top-tier competitive decks."
            ),
            DeckBox(
                name="Casual Decks",
                description="Fun and experimental decks for casual play."
            )
        ]
        db.session.add_all(deckboxes)
        db.session.commit()

        # Seed Decks
        decks = [
            Deck(
                name="Dark Moon EX",
                description="A strong dark-themed deck.",
                format="Standard",
                deckbox_id=deckboxes[0].id
            ),
            Deck(
                name="Ghost Control",
                description="A ghost-themed deck for control strategies.",
                format="Extended",
                deckbox_id=deckboxes[0].id
            ),
            Deck(
                name="Fun Energy Deck",
                description="A casual deck with quirky combos.",
                format="Casual",
                deckbox_id=deckboxes[1].id
            )
        ]
        db.session.add_all(decks)
        db.session.commit()

        # Seed Cards with set_id
        cards = [
            Card(
                name="Fezandipiti EX",
                type="Dark",
                set_id=sets[0].id  # Reference to Shrouded Fable
            ),
            Card(
                name="Dark Patch",
                type="Item",
                set_id=sets[0].id  # Reference to Shrouded Fable
            ),
            Card(
                name="Gengar EX",
                type="Ghost",
                set_id=sets[1].id  # Reference to Eclipse Shadow
            )
        ]
        db.session.add_all(cards)
        db.session.commit()

        # Seed DeckCards
        deckcards = [
            DeckCard(deck_id=decks[0].id, card_id=cards[0].id, quantity=4),
            DeckCard(deck_id=decks[0].id, card_id=cards[1].id, quantity=2),
            DeckCard(deck_id=decks[1].id, card_id=cards[2].id, quantity=3),
            DeckCard(deck_id=decks[2].id, card_id=cards[1].id, quantity=1)
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