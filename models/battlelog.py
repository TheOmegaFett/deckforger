
from sqlalchemy import Column, Integer, Boolean, JSON, ForeignKey
from init import db

class Battlelog(db.Model):
    """
    Represents a battle log entry in the database.
    
    This model stores statistics and outcomes from individual Pokemon TCG matches,
    tracking metrics like damage, card usage, and game duration.
    
    Attributes:
        id (int): Primary key identifier for the battle log
        deck_id (int): Foreign key linking to the deck used in battle
        win_loss (bool): True for win, False for loss
        total_turns (int): Number of turns the battle lasted
        most_used_cards (JSON): Array of frequently played cards during the match
        key_synergy_cards (JSON): Array of cards that created effective combinations
        damage_done (int): Total damage dealt to opponent
        damage_taken (int): Total damage received from opponent
        deck (relationship): Relationship to associated Deck model
    """
    
    __tablename__ = 'battlelogs'
    
    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey('decks.id'))
    win_loss = Column(Boolean)
    total_turns = Column(Integer)
    most_used_cards = Column(JSON)
    key_synergy_cards = Column(JSON)
    damage_done = Column(Integer)
    damage_taken = Column(Integer)
    
    deck = db.relationship("Deck", back_populates="battlelogs")

    def __repr__(self):
        return f"<Battlelog(deck_id={self.deck_id}, win={self.win_loss}, turns={self.total_turns})>"
