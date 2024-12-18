"""Format module for managing Pokemon TCG game formats and their rules.

This module defines the Format model, which represents different play formats
like Standard, Expanded, and Unlimited. Each format has specific rules about
which card sets are legal for play.
"""

from init import db


class Format(db.Model):
    """
    Represents a Pokémon Trading Card Game format.

    A format defines which cards are legal for tournament play based on 
    release dates and set legality. Examples include:

        - **Standard**: Newest sets only.
        - **Expanded**: Black & White forward.
        - **Unlimited**: All cards are legal.

    Attributes:
        id (int): Unique identifier for the format.
        name (str): Name of the format, must be unique (e.g., "Standard").
        description (str): Detailed rules and set restrictions for the format.
    """

    __tablename__ = 'formats'

    id = db.Column(db.Integer, primary_key=True, comment="Unique identifier for the format")
    name = db.Column(db.String(50), nullable=False, unique=True, comment="Name of the format (e.g., Standard)")
    description = db.Column(db.String(200), comment="Rules and set restrictions for the format")
    start_date = db.Column(db.DateTime, nullable=False, comment="Start date for format legality")

    def to_dict(self):
        """
        Convert Format object to dictionary representation.

        Returns:
            dict: Format data in dictionary format
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'start_date': self.start_date
        }

    def __repr__(self):
        """
        String representation of the Format.

        Returns:
            str: The name of the format enclosed in angle brackets.
        """
        return f"<Format {self.name}>"