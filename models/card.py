'''Card model for managing Pokemon TCG cards'''

# Third-party imports
from init import db
from models.cardset import CardSet


class Card(db.Model):
    """
    Represents a Pokemon Trading Card Game card.
    
    Attributes:
        id (int): Primary key for the card
        name (str): Name of the card
        type (str): Card type (Pokemon, Trainer, Energy)
        set_id (int): Foreign key reference to the set
        set (relationship): Relationship to the parent set
        decks (relationship): Relationship to associated decks
    """
    
    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'), nullable=False)
    card_type = db.Column(db.String(50))  # Discriminator column
    version = db.Column(db.Integer, default=1)
    
    __mapper_args__ = {
        'polymorphic_identity': 'card',
        'polymorphic_on': card_type
    }
    
    sets = db.relationship(CardSet, back_populates='cards')
    decks = db.relationship('DeckCard', back_populates='card', lazy='dynamic')
    variants = db.relationship('CardVariant', back_populates='card')

    def __repr__(self):
        return f'<Card {self.name}>'


class PokemonCard(Card):
    __tablename__ = 'pokemon_cards'
    
    id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    hp = db.Column(db.Integer)
    stage = db.Column(db.String(50))
    
    __mapper_args__ = {
        'polymorphic_identity': 'pokemon'
    }


class TrainerCard(Card):
    __tablename__ = 'trainer_cards'
    
    id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    trainer_type = db.Column(db.String(50))  # Item, Supporter, Stadium
    
    __mapper_args__ = {
        'polymorphic_identity': 'trainer'
    }


class EnergyCard(Card):
    __tablename__ = 'energy_cards'
    
    id = db.Column(db.Integer, db.ForeignKey('cards.id'), primary_key=True)
    energy_type = db.Column(db.String(50))
    is_basic = db.Column(db.Boolean, default=True)
    
    __mapper_args__ = {
        'polymorphic_identity': 'energy'
    }