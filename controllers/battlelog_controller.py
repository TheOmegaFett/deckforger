from flask import Blueprint, jsonify, request
from init import db
from models.battlelog import Battlelog
from models.deck import Deck
from schemas.battlelog_schema import battlelog_schema, battlelogs_schema

battlelogs = Blueprint('battlelogs', __name__, url_prefix='/battlelogs')

@battlelogs.route('/', methods=['GET'])
def get_battlelogs():
    battlelogs_list = Battlelog.query.all()
    return jsonify(battlelogs_schema.dump(battlelogs_list))

@battlelogs.route('/<int:id>', methods=['GET'])
def get_battlelog(id):
    battlelog = Battlelog.query.get_or_404(id)
    return jsonify(battlelog_schema.dump(battlelog))

@battlelogs.route('/deck/<int:deck_id>', methods=['GET'])
def get_deck_battlelogs(deck_id):
    deck_battlelogs = Battlelog.query.filter_by(deck_id=deck_id).all()
    return jsonify(battlelogs_schema.dump(deck_battlelogs))

@battlelogs.route('/', methods=['POST'])
def create_battlelog():
    battlelog_data = battlelog_schema.load(request.json)
    battlelog = Battlelog(**battlelog_data)
    db.session.add(battlelog)
    db.session.commit()
    return jsonify(battlelog_schema.dump(battlelog)), 201

@battlelogs.route('/stats/<int:deck_id>', methods=['GET'])
def get_deck_stats(deck_id):
    battlelogs = Battlelog.query.filter_by(deck_id=deck_id).all()
    
    if not battlelogs:
        return jsonify({"message": "No battle data found for this deck"}), 404
        
    total_games = len(battlelogs)
    wins = sum(1 for log in battlelogs if log.win_loss)
    
    stats = {
        "total_games": total_games,
        "wins": wins,
        "losses": total_games - wins,
        "win_rate": round((wins / total_games) * 100, 2),
        "avg_damage_dealt": round(sum(log.damage_done for log in battlelogs) / total_games),
        "avg_damage_taken": round(sum(log.damage_taken for log in battlelogs) / total_games),
        "avg_turns": round(sum(log.total_turns for log in battlelogs) / total_games)
    }
    
    return jsonify(stats)

@battlelogs.route('/import/<int:deck_id>', methods=['POST'])
def import_battlelog(deck_id):
    try:
        log_text = request.get_data(as_text=True)
        lines = log_text.split('\n')
        
        # Get deck to validate against
        deck = Deck.query.get_or_404(deck_id)
        deck_cards = {card.name for card in deck.cards}
        
        # Track cards played by each player
        player1_cards = set()
        player2_cards = set()
        current_player = None
        
        for line in lines:
            if "Turn #" in line:
                current_player = line.split("-")[1].strip().split("'")[0]
            elif "played" in line and "to" in line and current_player:
                card_name = line.split("played")[1].split("to")[0].strip()
                if current_player in line:
                    player1_cards.add(card_name)
                else:
                    player2_cards.add(card_name)
        
        # Validate card pools
        valid_log = (
            all(card in deck_cards for card in player1_cards) or 
            all(card in deck_cards for card in player2_cards)
        )
        
        if not valid_log:
            return jsonify({"error": "Battle log doesn't match specified deck"}), 400
            
        # Parse game data
        total_turns = len([line for line in lines if line.startswith('Turn #')])
        win_loss = "wins" in lines[-1]
        
        battlelog_data = {
            'deck_id': deck_id,
            'win_loss': win_loss,
            'total_turns': total_turns,
            'most_used_cards': list(player1_cards if len(player1_cards) > len(player2_cards) else player2_cards),
            'key_synergy_cards': [],
            'damage_done': 0,
            'damage_taken': 0
        }
        
        battlelog = Battlelog(**battlelog_data)
        db.session.add(battlelog)
        db.session.commit()
        
        return jsonify({
            "message": "Battle log imported successfully",
            "id": battlelog.id,
            "stats": battlelog_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "Failed to import battle log",
            "details": str(e)
        }), 500