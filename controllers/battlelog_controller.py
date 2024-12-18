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
        "avg_turns": round(sum(log.total_turns for log in battlelogs) / total_games)
    }
    return jsonify(stats)
   
@battlelogs.route('/import/<int:deck_id>/<string:player_name>', methods=['POST'])
def import_battlelog(deck_id, player_name):
    try:
        log_text = request.get_data(as_text=True)
        lines = log_text.split('\n')
    
        # Get deck to validate against
        deck = Deck.query.get_or_404(deck_id)
        deck_cards = {deckcard.card.name for deckcard in deck.deck_cards}
    
        # Track cards and interactions
        player_cards = set()
        opponent_cards = set()
        current_turn_player_cards = []  # Only track player's cards per turn
        card_interactions = {}
        current_player = None
        damage_done = 0
        damage_taken = 0

        card_usage_count = {}  # Track {card_name: usage_count}
        poisoned_pokemon = {}  # Initialize poisoned_pokemon dictionary

        def is_meaningful_interaction(card1, card2, line):
            # Define meaningful interactions
            interactions = [
                # Stadium sacrificed for attack
                (lambda c1, c2: "Stadium" in c1 and "discarded" in line and c2 in line and "used" in line),
                # Energy attachment and Pokemon
                (lambda c1, c2: "Energy" in c1 and "attached" in line and c2 in line),
                # Tool/Item card used on Pokemon
                (lambda c1, c2: ("Tool" in c1 or "Capsule" in c1) and "attached" in line and c2 in line)
            ]
            return any(check(card1, card2) or check(card2, card1) for check in interactions)

        for line in lines:
            if "Turn #" in line:
                current_player = line.split("-")[1].strip().split("'")[0]
        
            if current_player == player_name:
                # Check for meaningful interactions in each line
                for card1 in deck_cards:
                    for card2 in deck_cards:
                        if card1 != card2 and card1 in line and card2 in line:
                            if is_meaningful_interaction(card1, card2, line):
                                pair = tuple(sorted([card1, card2]))
                                card_interactions[pair] = card_interactions.get(pair, 0) + 1

            if "played" in line and "to" in line:
                card_name = line.split("played")[1].split("to")[0].strip()
                if current_player == player_name:
                    player_cards.add(card_name)
                    current_turn_player_cards.append(card_name)  # Only add player's cards
                else:
                    opponent_cards.add(card_name)
            elif "damage" in line:
                try:
                    # Track poison application
                    if "is now Poisoned" in line:
                        pokemon_name = line.split("'s")[1].split("is")[0].strip()
                        owner = line.split("'s")[0].strip()
                        poisoned_pokemon[pokemon_name] = {
                            'owner': owner,
                            'damage': 0
                        }
                
                    # Track poison removal/recovery
                    elif "recovered from all Special Conditions" in line or "is no longer" in line:
                        pokemon_name = line.split("'s")[1].split("has")[0].strip()
                        if pokemon_name in poisoned_pokemon:
                            owner = poisoned_pokemon[pokemon_name]['owner']
                            accumulated_damage = poisoned_pokemon[pokemon_name]['damage']
                            if owner == player_name:
                                damage_taken += accumulated_damage
                            else:
                                damage_done += accumulated_damage
                            del poisoned_pokemon[pokemon_name]
                
                    elif "damage" in line and "breakdown" not in line:
                        if "Total damage:" in line:
                            # Extract target Pokemon's owner
                            target_owner = line.split("'s")[0].strip()
                        
                            damage_text = line.split("Total damage:")[1].split("damage")[0]
                            damage_digits = ''.join(filter(str.isdigit, damage_text))
                            if damage_digits:
                                total_damage = int(damage_digits)
                                # Only count damage to opponent's Pokemon as damage_done
                                if current_player == player_name and target_owner != player_name:
                                    damage_done += total_damage
                                elif current_player != player_name and target_owner == player_name:
                                    damage_taken += total_damage
                        elif "took" in line:
                            # This captures self-inflicted damage like Frenzied Gouging
                            damage_text = line.split("took")[1].split("damage")[0]
                            damage_digits = ''.join(filter(str.isdigit, damage_text))
                            if damage_digits and current_player == player_name:
                                damage_taken += int(damage_digits)  # Will capture 200

                        # Poison damage tracking
                        if "damage counter" in line and "Poisoned" in line:
                            pokemon_name = line.split("'s")[1].split("for")[0].strip()
                            owner = line.split("'s")[0].strip()
                            if owner == player_name:
                                damage_taken += 10  # Each counter = 10 damage
                            else:
                                damage_done += 10  # Poison damage we deal

                except ValueError:
                    continue

            if current_player == player_name:
                # Extract card names from the line
                for card_name in deck_cards:  # Use deck_cards to check valid cards
                    if card_name in line:  # Check any mention of the card
                        card_usage_count[card_name] = card_usage_count.get(card_name, 0) + 1

        key_synergy_cards = sorted(card_interactions.items(), key=lambda x: x[1], reverse=True)[:3]
        key_synergy_cards = [list(pair[0]) for pair in key_synergy_cards]

        # Validate card pools against player name
        valid_log = all(card in deck_cards for card in player_cards)  # Using new variable name

        if not valid_log:
            return jsonify({"error": "Battle log doesn't match specified deck"}), 400

        # Clean the lines when we first get them
        lines = [line.strip() for line in log_text.split('\n') if line.strip()]

        total_turns = len([line for line in lines if line.startswith('Turn #')])

        # Then at the end, check the last actual line
        win_loss = any(
            condition in lines[-1] 
            for condition in [
                f"{player_name} wins",
                f"Opponent conceded. {player_name} wins"
            ]
        )

        # Get top 3 most used cards by usage count
        most_used = sorted(card_usage_count.items(), key=lambda x: x[1], reverse=True)[:3]
        most_used_cards = [card[0] for card in most_used]

        battlelog_data = {
            'deck_id': deck_id,
            'win_loss': win_loss,
            'total_turns': total_turns,
            'most_used_cards': most_used_cards,
            'key_synergy_cards': key_synergy_cards
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