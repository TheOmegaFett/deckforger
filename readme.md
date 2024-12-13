# Pokemon TCG Deck Builder API

A Flask-based REST API for managing Pokemon Trading Card Game decks, collections and formats.

## Features

- Deck Management (Create, store, and organize Pokemon TCG decks)
- Format Validation (Standard, Expanded, Unlimited)
- Card Database (Search and manage Pokemon cards)
- Deck Box Organization
- Deck Rating System

## Tech Stack

- Python
- Flask
- SQLAlchemy
- Marshmallow
- PostgreSQL

## Installation

1. Clone the repository
2. Create and activate virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables in .env file
5. Initialize database:

```bash
flask run/create
flask run/seed
```

## API Endpoints

Decks

- GET /api/decks - List all decks
- POST /api/decks - Create new deck
- GET /api/decks/{id} - Get deck details
- PUT /api/decks/{id} - Update deck
- DELETE /api/decks/{id} - Delete deck
  Cards
- GET /api/cards - List all cards
- POST /api/cards - Add new card
- GET /api/cards/{id} - Get card details
- PUT /api/cards/{id} - Update card
- DELETE /api/cards/{id} - Delete card

[Additional endpoint sections...]

## Database Schema

![Pokemon TCG Deck Builder ERD](docs/erd2.png)

## Usage Examples

### Creating a New Deck

```python
# Create a Standard format deck
POST /api/decks
{
    "name": "Charizard Control",
    "description": "Fire-type control deck",
    "format_id": 1
}
```

### Adding Cards to a Deck

```python
# Add cards with quantities
POST /api/decks/{deck_id}/cards
[
    {
        "card_id": 5,
        "quantity": 4
    },
    {
        "card_id": 11,
        "quantity": 20
    }
]
```

### Rating a Deck

```python
# Add a rating with comment
POST /api/decks/{deck_id}/ratings
{
    "score": 5,
    "comment": "Great deck composition!"
}
```

### Searching Cards

```python
# Search for Fire-type cards
GET /api/cards/search?type=fire

# Search by set
GET /api/cards/search?set_id=1
```

### Managing Deck Boxes

```python
# Create a new deck box
POST /api/deckboxes
{
    "name": "Tournament Decks",
    "description": "Competition-ready decks"
}

# Add deck to deck box
POST /api/deckboxes/{deckbox_id}/decks
{
    "name": "Championship Deck",
    "format": "Standard"
}
```

### Format Validation

```python
# Validate deck format legality
GET /api/decks/validate/{deck_id}
```

## Contributing

Development is ongoing. Contributions are welcome! But please allow for grading before accept pull requests.

Main Developer: Shane W Miller

## License

Copyright (c) 2024 Shane W Miller

Permission is granted, free of charge, to use this software solely for educational purposes as part of Coder Academy coursework and assessment requirements.

All other rights are reserved. This software may not be:

- Used for commercial purposes
- Modified or distributed outside of educational requirements
- Used in any way not directly related to course assessments

Any use of this software must maintain this copyright notice and license terms.

For permissions beyond educational use, contact [Your Contact Information].
