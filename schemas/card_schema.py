'''Schema for serializing and deserializing Pokemon TCG cards'''

from init import ma
from marshmallow import validates, ValidationError
from models.card import Card, PokemonCard, TrainerCard, EnergyCard

class CardSchema(ma.SQLAlchemySchema):
    """Base schema for Card model serialization"""
    
    class Meta:
        model = Card
        include_fk = True

    id = ma.auto_field()
    name = ma.auto_field(required=True)
    type = ma.auto_field(required=True)
    set_id = ma.auto_field(required=True)
    card_type = ma.auto_field()
    version = ma.auto_field()
    variants = ma.Nested('CardVariantSchema', many=True)

class PokemonCardSchema(CardSchema):
    """Schema for Pokemon card type"""
    
    class Meta:
        model = PokemonCard

    hp = ma.auto_field()
    stage = ma.auto_field()

class TrainerCardSchema(CardSchema):
    """Schema for Trainer card type"""
    
    class Meta:
        model = TrainerCard

    trainer_type = ma.auto_field()

class EnergyCardSchema(CardSchema):
    """Schema for Energy card type"""
    
    class Meta:
        model = EnergyCard

    energy_type = ma.auto_field()
    is_basic = ma.auto_field()

# Schema instances
card_schema = CardSchema()
cards_schema = CardSchema(many=True)
pokemon_schema = PokemonCardSchema()
pokemons_schema = PokemonCardSchema(many=True)
trainer_schema = TrainerCardSchema()
trainers_schema = TrainerCardSchema(many=True)
energy_schema = EnergyCardSchema()
energies_schema = EnergyCardSchema(many=True)
