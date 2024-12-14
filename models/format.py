"""Format module for managing Pokemon TCG game formats and their rules.

This module defines the Format model which represents different play formats
like Standard, Expanded, and Unlimited. Each format has specific rules about
which card sets are legal for play.
"""

from init import db


class Format(db.Model):
    """Represents a Pokemon Trading Card Game format.
    
    A format defines which cards are legal for tournament play based on 
    release dates and set legality. Examples include Standard (newest sets),
    Expanded (Black & White forward), and Unlimited (all cards).
    
    Attributes:
        id (int): Unique identifier for the format
        name (str): Name of the format, must be unique (e.g. "Standard")
        description (str): Detailed rules and set restrictions for the format
    """
    
    __tablename__ = 'formats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))

    def __repr__(self):
        """String representation of the Format.
        
        Returns:
            str: Format name in angle brackets
        """
        return f'<Format {self.name}>'