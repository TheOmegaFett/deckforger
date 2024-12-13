from init import db, ma
from flask import Flask
import os
from controllers.deck_controller import deck_controller
from controllers.deckbox_controller import deckbox_controller
from controllers.cli_controller import cli_controller
from controllers.card_controller import card_controller
from controllers.deckcard_controller import deckcard_controller
from controllers.cardset_controller import cardset_controller
from controllers.format_controller import format_blueprint
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    
    load_dotenv()  
    
    # Load environment variables from .env
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")
    app.config['SQLALCHEMY_ECHO'] = True  # This will show SQL output
    
    
    url = os.environ.get("DATABASE_URI")
    print(url)
    
    app.json.sort_keys = False
    
    # Initialize extensions
    db.init_app(app)
    # with app.app_context():
    #     db.create_all()
    ma.init_app(app)
    # migrate.init_app(app, db)
    
    # Register blueprints
    app.register_blueprint(cli_controller)
    app.register_blueprint(deck_controller, url_prefix="/api/decks")
    app.register_blueprint(deckbox_controller, url_prefix="/api/deckboxes")
    app.register_blueprint(card_controller, url_prefix="/api/cards")
    app.register_blueprint(deckcard_controller, url_prefix="/api/deckcards")
    app.register_blueprint(cardset_controller, url_prefix="/api/cardsets")
    app.register_blueprint(format_blueprint)
   
    return app

# For Gunicorn or Flask CLI
app = create_app()

# Ensure app context is pushed at start
if __name__ != "__main__":
    with app.app_context():
        pass  # Push the app context to ensure no errors on imports