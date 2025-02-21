from datetime import datetime, timezone
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from flask import Blueprint, request, jsonify
from init import db
from models.battlelog import Battlelog
from models.deck import Deck
from schemas import analyses_schema
from schemas.ai_analysis_schema import ai_analysis_schema

from models.ai_analysis import AIAnalysis


ai_analysis_controller = Blueprint('ai_analysis', __name__)

class DeckAnalysisEngine:
    def __init__(self):
        self.model = RandomForestClassifier()
        self.is_trained = False
        print("Analysis engine initialized")  # Verify initialization    
    def train_on_all_logs(self):
        """Train the model using all available battle logs"""
        logs = Battlelog.query.all()
        
        X = []  # Features
        y = []  # Outcomes (win/loss)
        
        for log in logs:
            features = self._extract_features(log)
            X.append(features)
            y.append(1 if log.win_loss else 0)
        
        if X and y:
            self.model.fit(np.array(X), np.array(y))
            self.is_trained = True
            
    def _extract_features(self, log):
        """Extract relevant features from a battle log"""
        return [
            log.total_turns,
            len(log.most_used_cards),
            len(log.key_synergy_cards),
        ]

    def _calculate_avg_turns(self, logs):
        if not logs:
            return {
                'average': 0,
                'median': 0,
                'trend': 'insufficient_data'
            }
        turns = [log.total_turns for log in logs]
        trend = 'stable'
        if len(turns) > 1:
            trend = 'increasing' if turns[-1] > turns[0] else 'decreasing' if turns[-1] < turns[0] else 'stable'
        
        return {
            'average': float(np.mean(turns)),
            'median': float(np.median(turns)),
            'trend': trend
        }

    def analyze_deck(self, deck_id):
        deck = Deck.query.get(deck_id)
        self.deck = deck
        # Store deck_logs as class attribute
        self.deck_logs = Battlelog.query.filter_by(deck_id=deck_id).all()

        # Calculate average turns first and ensure it's a float
        avg_turns_data = self._calculate_avg_turns(self.deck_logs)
        if isinstance(avg_turns_data, (int, float)):
            average_turns = float(avg_turns_data)
        else:
            average_turns = float(avg_turns_data['average'])

        # Get card performance data
        card_performance = self._identify_key_cards(self.deck_logs)
        weak_performers = self._identify_weak_performers(card_performance, deck, self.deck_logs)

        # Store card effectiveness data in performance_metrics
        performance_metrics = {
            'key_cards': card_performance,
            'underperforming_cards': weak_performers['underperforming_cards'],
            'coin_flip_cards': weak_performers['coin_flip_stats'],
            'unused_cards': weak_performers['unused_cards']
        }

        # Prepare analysis with valid model fields
        analysis = {
            'deck_id': deck_id,
            'timestamp': datetime.now(timezone.utc),
            'win_rate': float(self._calculate_win_rate(self.deck_logs)),
            'total_battles': len(self.deck_logs),
            'average_turns': average_turns,
            'performance_metrics': performance_metrics,
            'trend_analysis': self._analyze_performance_trend(self.deck_logs)
        }
        
        print(f"Generated analysis: {analysis}")  # Verify analysis object
        
        return analysis

   
    def _find_unused_cards(self, card_performance):
        deck_cards = set(deck_card.card.name for deck_card in self.deck.deck_cards)
        used_cards = set()
        
        # Track all cards that appear in battle logs
        for log in self.deck_logs:  # Need to store deck_logs as class attribute
            for card in log.most_used_cards:
                used_cards.add(card)
                
        # Calculate usage threshold
        total_games = len(self.deck_logs)
        usage_threshold = max(1, total_games * 0.1)  # Lower threshold
        
        rarely_used = []
        for card in deck_cards:
            if card not in used_cards:
                rarely_used.append({'card': card})
                
        return rarely_used


    def _identify_weak_performers(self, card_performance, deck, deck_logs):
        weak_performers = []
        total_games = len(deck_logs)

        for card_name, stats in card_performance['most_used']:
            if (stats['uses'] >= total_games * 0.15 and
                (stats['wins'] / stats['uses']) < 0.45):
                weak_performers.append({
                    'card': card_name,
                    'win_rate': (stats['wins'] / stats['uses']) * 100,
                    'uses': stats['uses']
                })

        # Add default message if no weak performers found
        if not weak_performers:
            weak_performers = [{"message": "All frequently used cards are performing effectively"}]

        return {
            'underperforming_cards': weak_performers,
            'coin_flip_stats': self._analyze_coin_flip_cards(deck_logs),
            'unused_cards': self._find_unused_cards(card_performance)
        }

    def _analyze_coin_flip_cards(self, logs):
        """Analyze success rates of coin flip dependent cards"""
        coin_flip_stats = {
            "Crushing Hammer": {"attempts": 0, "successes": 0},
            "Super Scoop Up": {"attempts": 0, "successes": 0}
        }

        for log in logs:
            raw_log = log.raw_log.lower()
        
            # Track Crushing Hammer
            if "crushing hammer" in raw_log:
                hammer_attempts = raw_log.count("played crushing hammer")
                coin_flip_stats["Crushing Hammer"]["attempts"] += hammer_attempts
                successes = raw_log.count("landed on heads")
                coin_flip_stats["Crushing Hammer"]["successes"] += successes
            
            # Track Super Scoop Up
            if "super scoop up" in raw_log:
                scoop_attempts = raw_log.count("played super scoop up")
                coin_flip_stats["Super Scoop Up"]["attempts"] += scoop_attempts
                successes = raw_log.count("returned to hand")
                coin_flip_stats["Super Scoop Up"]["successes"] += successes

        # Calculate success rates
        for card in coin_flip_stats:
            stats = coin_flip_stats[card]
            if stats["attempts"] > 0:
                stats["success_rate"] = (stats["successes"] / stats["attempts"]) * 100
            else:
                stats["success_rate"] = 0

        return coin_flip_stats
    
    def _calculate_win_rate(self, logs):
        """Calculate win rate with statistical confidence"""
        if not logs:
            return 0.0
        wins = sum(1 for log in logs if log.win_loss)
        return (wins / len(logs)) * 100

    def _calculate_avg_turns(self, logs):
        """Calculate average turns with trend analysis"""
        if not logs:
            return {
                'average': 0,
                'median': 0,
                'trend': 'insufficient_data'
            }
        turns = [log.total_turns for log in logs]
        return {
            'average': np.mean(turns),
            'median': np.median(turns),
            'trend': 'increasing' if np.polyfit(range(len(turns)), turns, 1)[0] > 0 else 'decreasing'
        }
    def _identify_key_cards(self, logs):
        """Analyze card effectiveness with minimum game threshold"""
        MIN_GAMES_THRESHOLD = 3  # Minimum games needed for effectiveness ranking

        card_stats = {}
        for log in logs:
            for card in log.most_used_cards:
                if card not in card_stats:
                    card_stats[card] = {'uses': 0, 'wins': 0}
                card_stats[card]['uses'] += 1
                if log.win_loss:
                    card_stats[card]['wins'] += 1

        # Filter cards that meet minimum threshold
        qualified_cards = {
            card: stats for card, stats in card_stats.items() 
            if stats['uses'] >= MIN_GAMES_THRESHOLD
        }

        return {
            'most_effective': sorted(
                qualified_cards.items(),
                key=lambda x: x[1]['wins'] / x[1]['uses'],
                reverse=True
            )[:3],
            'most_used': sorted(
                card_stats.items(),
                key=lambda x: x[1]['uses'],
                reverse=True
            )[:3]
        }
    def _analyze_matchups(self, logs):
        """Analyze performance against different strategies"""
        matchup_stats = {}
        for log in logs:
            strategy = self._identify_opponent_strategy(log)
            if strategy not in matchup_stats:
                matchup_stats[strategy] = {'games': 0, 'wins': 0}
            matchup_stats[strategy]['games'] += 1
            if log.win_loss:
                matchup_stats[strategy]['wins'] += 1
        
        return {
            strategy: {
                'win_rate': (stats['wins'] / stats['games']) * 100,
                'total_games': stats['games']
            }
            for strategy, stats in matchup_stats.items()
        }

    def _identify_opponent_strategy(self, log):
        """Identify opponent's deck strategy based on card patterns in the raw log"""
        # Define strategy patterns to look for in the raw log
        strategies = {
            'aggro': ['attack', 'damage', 'knockout'],
            'control': ['discard', 'energy removal', 'hammer'],
            'combo': ['search', 'draw', 'evolution'],
            'stall': ['heal', 'switch', 'recovery']
        }
    
        # Parse the raw log for strategy indicators
        strategy_scores = {
            name: sum(1 for pattern in patterns if pattern in log.raw_log.lower())
            for name, patterns in strategies.items()
        }
    
        # Return the strategy with highest score, default to 'unknown'
        if not strategy_scores:
            return 'unknown'
    
        return max(strategy_scores.items(), key=lambda x: x[1])[0]

   

     
    def _generate_suggestions(self, logs, deck):
        """Generate deck improvement suggestions based on performance data"""
        suggestions = {
            'card_recommendations': [],
            'strategy_tips': [],
            'sideboard_suggestions': []
        }

        card_performance = self._identify_key_cards(logs)
        # Add the deck parameter here
        weak_cards = self._identify_weak_performers(card_performance, deck)

        suggestions['card_recommendations'] = [
            f"Consider replacing {card} with {alternative}"
            for card, alternative in self._get_card_alternatives(weak_cards)
        ]

        matchups = self._analyze_matchups(logs)
        suggestions['strategy_tips'] = self._generate_strategy_tips(matchups)

        return suggestions

   
    def _generate_strategy_tips(self, matchups):
        """Generate strategic advice based on matchup analysis"""
        tips = []

        for strategy, stats in matchups.items():
            win_rate = stats['win_rate']
            if win_rate < 45:
                if strategy == 'aggro':
                    tips.append("Add more defensive cards to counter aggressive strategies")
                elif strategy == 'control':
                    tips.append("Include more energy acceleration to overcome energy denial")
                elif strategy == 'combo':
                    tips.append("Add more disruption cards to break their combo pieces")
                elif strategy == 'stall':
                    tips.append("Include more consistent damage output cards")
            
        return tips

    def _determine_card_category(self, card_name):
        """Helper method to categorize cards by their primary function"""
        # Simple categorization logic - could be expanded with more sophisticated rules
        if 'V' in card_name or 'VMAX' in card_name:
            return 'basic_attacker'
        elif 'energy' in card_name.lower():
            return 'energy_acceleration'
        else:
            return 'support'

    def _analyze_performance_trend(self, logs):
        if not logs:
            return {
                'trend': 'No games played yet',
                'consistency_score': 0.0,
                'recent_win_rate': 0.0,
                'first_turn_win_rate': 0.0,
                'second_turn_win_rate': 0.0
            }

        # Explicitly check went_first flag
        first_turn_games = [log for log in logs if log.went_first is True]
        second_turn_games = [log for log in logs if log.went_first is False]

        first_turn_wr = (
            sum(1 for g in first_turn_games if g.win_loss) / len(first_turn_games)
            if first_turn_games else 0.0
        ) * 100  # Convert to percentage

        second_turn_wr = (
            sum(1 for g in second_turn_games if g.win_loss) / len(second_turn_games)
            if second_turn_games else 0.0
        ) * 100  # Convert to percentage

        recent_games = logs[-3:] if len(logs) >= 3 else logs
        recent_wr = (sum(1 for g in recent_games if g.win_loss) / len(recent_games)) * 100

        overall_wr = (sum(1 for g in logs if g.win_loss) / len(logs)) * 100
        trend = (
            'improving' if recent_wr > overall_wr
            else 'declining' if recent_wr < overall_wr
            else 'stable'
        )

        return {
            'trend': trend,
            'consistency_score': float(np.std([g.win_loss for g in logs])),
            'recent_win_rate': recent_wr,
            'first_turn_win_rate': first_turn_wr,
            'second_turn_win_rate': second_turn_wr
        }
@ai_analysis_controller.route('/<int:deck_id>', methods=['GET'])
def analyze_deck_performance(deck_id):
    # Add logging
    print(f"Analyzing deck {deck_id}")

    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        analysis_engine = DeckAnalysisEngine()
        analysis_results = analysis_engine.analyze_deck(deck_id)

        if not analysis_results:
            return jsonify({'error': 'Analysis produced no results'}), 500

        # Add result logging
        print(f"Analysis results: {analysis_results}")

        return jsonify(analysis_results), 200

    except Exception as e:
        print(f"Analysis error: {str(e)}")  # Debug logging
        return jsonify({
            'error': 'Failed to analyze deck performance', 
            'details': str(e)
        }), 500


@ai_analysis_controller.route('/deck/<int:deck_id>/history', methods=['GET'])
def get_analysis_history(deck_id):
    """Retrieve historical analysis data for a deck"""
    try:
        analyses = AIAnalysis.query.filter_by(deck_id=deck_id).order_by(AIAnalysis.timestamp.desc()).all()
        result = ai_analysis_schema.dump(analyses)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve analysis history', 'details': str(e)}), 500
