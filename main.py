'''Main application configuration and initialization'''

from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
import os
from init import db, ma
from controllers.deck_controller import deck_controller
from controllers.deckbox_controller import deckbox_controller
from controllers.cli_controller import cli_controller
from controllers.card_controller import card_controller
from controllers.deckcard_controller import deckcard_controller
from controllers.cardset_controller import cardset_controller
from controllers.format_controller import format_controller
from controllers.cardtype_controller import cardtype_controller
from controllers.battlelog_controller import battlelogs
from controllers.rating_controller import rating_controller
from controllers.ai_analysis_controller import ai_analysis_controller

# Load environment variables first, before any app creation
load_dotenv()

def create_app():
    """
    Creates and configures the Flask application.
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    # Get database URI from environment
    load_dotenv()
    database_uri = os.environ.get('DATABASE_URI')
    print(f"Main.py DATABASE_URI: {os.environ.get('DATABASE_URI')}")
    
    app.config.update(
        SQLALCHEMY_DATABASE_URI=database_uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        
    )
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Register blueprints
    app.register_blueprint(cli_controller)
    app.register_blueprint(deck_controller, url_prefix='/api/decks')
    app.register_blueprint(deckbox_controller, url_prefix='/api/deckboxes')
    app.register_blueprint(card_controller, url_prefix='/api/cards')
    app.register_blueprint(deckcard_controller, url_prefix='/api/deckcards')
    app.register_blueprint(cardset_controller, url_prefix='/api/cardsets')
    app.register_blueprint(format_controller, url_prefix='/api/formats')
    app.register_blueprint(cardtype_controller, url_prefix='/api/cardtypes')
    app.register_blueprint(battlelogs, url_prefix='/api/battlelogs')
    app.register_blueprint(rating_controller, url_prefix='/api/ratings')
    app.register_blueprint(ai_analysis_controller, url_prefix='/api/analysis')    
    return app

# Create application instance
app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()
