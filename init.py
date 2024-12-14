"""
Database and extension initialization module for Deckforger.

This module sets up SQLAlchemy for database operations, 
Marshmallow for serialization/deserialization,
and Flask-Migrate for database migrations.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate

# Database instance for model definitions and queries
db = SQLAlchemy()

# Marshmallow instance for schema serialization
ma = Marshmallow()

# Migration instance for database version control
migrate = Migrate()
