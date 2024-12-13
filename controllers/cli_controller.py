from flask import jsonify
from flask import Blueprint
from init import db
from models import Card, Deck, DeckBox, DeckCard, CardSet

cli_controller = Blueprint("cli", __name__)

@cli_controller.route("/run/create", methods=["POST"])
def create_tables():
    db.create_all()
    return jsonify({"message": "Tables created successfully!"})

@cli_controller.route("/run/seed", methods=["POST"])
def seed_tables():
    # Example data for seeding
    
    cardset1 = CardSet(name="Base Set", description="The original set of cards.")
    db.session.add(cardset1)
    db.session.commit()
    
    cardset2 = CardSet(name="Expansion Set", description="Additional cards added later.")
    db.session.add(cardset2)
    db.session.commit()
    
    deckbox = DeckBox(name="Competitive Decks", description="Top tier decks.")
    db.session.add(deckbox)
    db.session.commit()

    card = Card(name="Fezandipiti EX", type="Dark", set_id=1)
    db.session.add(card)
    db.session.commit()

    return jsonify({"message": "Database seeded successfully!"})

@cli_controller.route('/health')
def health_check():
    return jsonify({"status": "API is running!"}), 200

@cli_controller.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created!")
    
@cli_controller.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@cli_controller.cli.command("seed")
def seed_tables():
    
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