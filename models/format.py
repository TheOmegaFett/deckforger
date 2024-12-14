'''Format model for managing Pokemon TCG game formats'''

# Third-party imports
from init import db


class Format(db.Model):
    """
    Represents a Pokemon Trading Card Game format.
    
    Attributes:
        id (int): Primary key for the format
        name (str): Name of the format, must be unique
        description (str): Description of the format rules
    """
    
    __tablename__ = 'formats'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def __repr__(self):
        return f'<Format {self.name}>'


