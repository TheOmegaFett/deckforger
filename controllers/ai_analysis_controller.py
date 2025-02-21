from datetime import datetime, timezone
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from flask import Blueprint, json, jsonify
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
        self.deck = deck  # Store deck reference for analysis methods
        deck_logs = Battlelog.query.filter_by(deck_id=deck_id).all()

        # Calculate average turns first and ensure it's a float
        avg_turns_data = self._calculate_avg_turns(deck_logs)
        if isinstance(avg_turns_data, (int, float)):
            average_turns = float(avg_turns_data)
        else:
            average_turns = float(avg_turns_data['average'])

        # Get card performance data
        card_performance = self._identify_key_cards(deck_logs)
        # Updated call with deck parameter
        weak_performers = self._identify_weak_performers(card_performance, deck)

        # Prepare analysis with type-safe values
        analysis = {
            'deck_id': deck_id,
            'timestamp': datetime.now(timezone.utc),
            'win_rate': float(self._calculate_win_rate(deck_logs)),
            'total_battles': len(deck_logs),
            'average_turns': average_turns,
            'performance_metrics': card_performance,
            'trend_analysis': self._analyze_performance_trend(deck_logs),
            'card_effectiveness': {
                'underperforming_cards': weak_performers['underperforming_cards'],
                'coin_flip_cards': weak_performers['coin_flip_stats'],
                'unused_cards': weak_performers['unused_cards']
            },
            'suggestions': self._generate_suggestions(deck_logs, deck)
        }

        ai_analysis = AIAnalysis(**analysis)
        db.session.add(ai_analysis)
        db.session.commit()

        return analysis

    def _identify_weak_performers(self, card_performance, deck):  # Added deck parameter
        """Identify cards with poor performance metrics"""
        weak_performers = []
        
        for card_stats in card_performance['most_used']:
            card_name, stats = card_stats
            # Consider a card weak if used frequently but has < 40% win rate
            if stats['uses'] >= 5 and (stats['wins'] / stats['uses']) < 0.4:
                weak_performers.append({
                    'card': card_name,
                    'win_rate': (stats['wins'] / stats['uses']) * 100,
                    'uses': stats['uses']
                })
                
        # Track coin flip dependent cards
        coin_flip_cards = {
            'Crushing Hammer': {'success_rate': 0, 'attempts': 0},
            'Super Scoop Up': {'success_rate': 0, 'attempts': 0}
        }
        
        return {
            'underperforming_cards': weak_performers,
            'coin_flip_stats': coin_flip_cards,
            'unused_cards': self._find_unused_cards(card_performance)  # Remove deck parameter here
        }

    def _find_unused_cards(self, card_performance):  # Remove deck parameter here
        """Find cards that were rarely or never used"""
        deck_cards = set(card.name for card in self.deck.cards)
        used_cards = set(card for card, stats in card_performance['most_used'])
        
        rarely_used = []
        for card in deck_cards - used_cards:
            rarely_used.append({
                'card': card,
                'recommendation': self._get_replacement_suggestion(card)
            })
        
        return rarely_used

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
    def _identify_weak_performers(self, card_performance, deck):  # Added deck parameter
        """Identify cards with poor performance metrics"""
        weak_performers = []
        
        for card_stats in card_performance['most_used']:
            card_name, stats = card_stats
            # Consider a card weak if used frequently but has < 40% win rate
            if stats['uses'] >= 5 and (stats['wins'] / stats['uses']) < 0.4:
                weak_performers.append({
                    'card': card_name,
                    'win_rate': (stats['wins'] / stats['uses']) * 100,
                    'uses': stats['uses']
                })
                
        # Track coin flip dependent cards
        coin_flip_cards = {
            'Crushing Hammer': {'success_rate': 0, 'attempts': 0},
            'Super Scoop Up': {'success_rate': 0, 'attempts': 0}
        }
        
        return {
            'underperforming_cards': weak_performers,
            'coin_flip_stats': coin_flip_cards,
            'unused_cards': self._find_unused_cards(card_performance)  # Remove deck parameter
        }

    def _find_unused_cards(self, card_performance):
        """Find cards that were rarely or never used"""
        # Access card names through the card relationship on DeckCard
        deck_cards = set(deck_card.card.name for deck_card in self.deck.deck_cards)
        used_cards = set(card for card, stats in card_performance['most_used'])
        
        rarely_used = []
        for card in deck_cards - used_cards:
            rarely_used.append({
                'card': card,
                'recommendation': self._get_replacement_suggestion(card)
            })
        
        return rarely_used

    def _get_replacement_suggestion(self, card):
        """Generate contextual replacement suggestions"""
        # Add card category mapping
        card_categories = {
            'Crushing Hammer': 'disruption',
            'Super Scoop Up': 'recovery',
            # Add more categories
        }
        
        category = card_categories.get(card, 'general')
        alternatives = {
            'disruption': ['Team Skull Grunt', 'Enhanced Hammer'],
            'recovery': ['Scoop Up Net', 'Switch'],
            'general': ['Professor\'s Research', 'Marnie']
        }
        
        return alternatives.get(category, [])[0]    
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

    def _get_card_alternatives(self, weak_cards):
        """Generate alternative card suggestions based on deck performance data"""
        # Simulated card alternatives for demonstration
        card_alternatives = {
            'basic_attacker': ['Mewtwo V', 'Zacian V', 'Charizard VMAX'],
            'energy_acceleration': ['Frosmoth', 'Rose', 'Welder'],
            'support': ["Professor's Research", "Marnie", "Boss's Orders"]
        }

        suggestions = []
        for card in weak_cards:
            # Match card to a category and suggest top performers
            category = self._determine_card_category(card)
            if category in card_alternatives:
                suggestions.append((card, card_alternatives[category][0]))
        
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

    def _calculate_avg_turns(self, logs):
        if not logs:
            return {
                'average': 0,
                'median': 0,
                'trend': 'insufficient_data'
            }
        turns = [log.total_turns for log in logs]
        return {
            'average': float(np.mean(turns)),
            'median': float(np.median(turns)),
            'trend': 'stable' if len(turns) < 2 else ('increasing' if turns[-1] > turns[0] else 'decreasing')
        }

    def _analyze_performance_trend(self, logs):
        """Analyze performance trends using 3-game window"""
        if not logs:
            return {
                'trend': 'No games played yet',
                'consistency_score': 0.0,
                'recent_win_rate': 0.0,
                'first_turn_win_rate': 0.0,
                'second_turn_win_rate': 0.0
            }

        # Calculate first/second turn stats
        first_turn_games = [log for log in logs if log.went_first]
        second_turn_games = [log for log in logs if not log.went_first]
    
        first_turn_wr = (
            sum(1 for g in first_turn_games if g.win_loss) / len(first_turn_games)
            if first_turn_games else 0.0
        )
    
        second_turn_wr = (
            sum(1 for g in second_turn_games if g.win_loss) / len(second_turn_games)
            if second_turn_games else 0.0
        )

        # Use 3-game window for trend
        recent_games = logs[-3:] if len(logs) >= 3 else logs
        recent_wr = sum(1 for g in recent_games if g.win_loss) / len(recent_games)

        # Compare recent performance to overall
        overall_wr = sum(1 for g in logs if g.win_loss) / len(logs)
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
    """
    Analyze deck performance using battle logs and AI.
    
    Parameters:
        deck_id (int): ID of the deck to analyze
        
    Returns:
        200: Analysis results in JSON format
        404: Deck not found
        500: Analysis operation failed
    """
    try:
        deck = db.session.get(Deck, deck_id)
        if not deck:
            return jsonify({'error': 'Deck not found'}), 404

        analysis_engine = DeckAnalysisEngine()
        analysis_results = analysis_engine.analyze_deck(deck_id)

        return jsonify(analysis_results), 200

    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze deck performance', 
            'details': str(e)
        }), 500

@ai_analysis_controller.route('/deck/<int:deck_id>/history', methods=['GET'])
def get_analysis_history(deck_id):
    """Retrieve historical analysis data for a deck"""
    try:
        analyses = AIAnalysis.query.filter_by(deck_id=deck_id).order_by(AIAnalysis.timestamp.desc()).all()
        return analyses_schema.jsonify(analyses), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve analysis history', 'details': str(e)}), 500

