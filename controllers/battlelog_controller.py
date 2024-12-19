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
    
    # Check if either player's card pool matches the deck
    valid_log = (
        all(card in deck_cards for card in player1_cards) or 
        all(card in deck_cards for card in player2_cards)
    )
    
    if not valid_log:
        return jsonify({"error": "Battle log doesn't match specified deck"}), 400
    
    # Initialize tracking
    current_turn_cards = []
    card_interactions = {}
    
    for line in lines:
        if line.startswith('Turn #'):
            # Process previous turn's interactions
            for i, card1 in enumerate(current_turn_cards):
                for card2 in current_turn_cards[i+1:]:
                    pair = tuple(sorted([card1, card2]))
                    card_interactions[pair] = card_interactions.get(pair, 0) + 1
            current_turn_cards = []
        
        elif "played" in line or "used" in line:
            card_name = line.split("played")[1].split("to")[0].strip() if "played" in line else line.split("used")[0].strip()
            current_turn_cards.append(card_name)
    
    # Get top synergy pairs
    key_synergy_cards = sorted(card_interactions.items(), key=lambda x: x[1], reverse=True)[:3]
    key_synergy_cards = [list(pair[0]) for pair in key_synergy_cards]
    
    # Parse total turns
    turns = [line for line in lines if line.startswith('Turn #')]
    total_turns = len(turns)
    
    # Parse win/loss from final line
    win_loss = "wins" in lines[-1]
    
    # Track card usage frequency
    card_counts = {}
    for line in lines:
        if "played" in line and "to" in line:
            card_name = line.split("played")[1].split("to")[0].strip()
            card_counts[card_name] = card_counts.get(card_name, 0) + 1
    
    # Get most used cards (top 5)
    most_used_cards = sorted(card_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    most_used_cards = [card[0] for card in most_used_cards]
    
    # Calculate damage stats
    damage_done = 0
    damage_taken = 0
    for line in lines:
        if "damage" in line and "breakdown" not in line:
            damage_amount = int(''.join(filter(str.isdigit, line.split("damage")[0])))
            if "on" in line:  # Damage dealt to opponent
                damage_done += damage_amount
            else:  # Damage taken
                damage_taken += damage_amount
    
    # Create initial battlelog entry
    battlelog_data = {
        'deck_id': deck_id,
        'win_loss': win_loss,
        'total_turns': total_turns,
        'most_used_cards': most_used_cards,
        'key_synergy_cards': key_synergy_cards,
        'damage_done': damage_done,
        'damage_taken': damage_taken
    }
    
    battlelog = Battlelog(**battlelog_data)
    db.session.add(battlelog)
    db.session.commit()
    
    return jsonify({
        "message": "Battle log imported successfully", 
        "id": battlelog.id,
        "raw_log": log_text,
        "stats": battlelog_data
    }), 201