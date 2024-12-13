from init import ma
from models.card import Card
from models.deck import Deck
from datetime import datetime
from marshmallow import validates, ValidationError
from models.cardset import CardSet
from models.deckcard import DeckCard

class DeckSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Deck

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
    format_id = ma.auto_field(required=True)  # Only format_id included
    cards = ma.Nested("DeckCardSchema", only=["id", "quantity"], many=True)

    @validates('format_id')
    def validate_deck_format(self, format_id):
        # Get all cards in the deck through DeckCards
        deck_cards = DeckCard.query.filter_by(deck_id=self.id).all()
        
        # Define format date boundaries
        standard_date = datetime(2022, 7, 1)  # Sword & Shield forward
        expanded_date = datetime(2011, 9, 1)  # Black & White forward
        
        for deck_card in deck_cards:
            card = Card.query.get(deck_card.card_id)
            card_set = CardSet.query.get(card.set_id)
            
            if format_id == 1:  # Standard
                if card_set.release_date < standard_date:
                    raise ValidationError(
                        f"Card {card.name} from set {card_set.name} is not legal in Standard format"
                    )
            elif format_id == 2:  # Expanded
                if card_set.release_date < expanded_date:
                    raise ValidationError(
                        f"Card {card.name} from set {card_set.name} is not legal in Expanded format"
                    )
            # Format 3 is Unlimited, all cards allowed
