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

    def analyze_deck(self, deck_id):
        deck = Deck.query.get(deck_id)
        deck_logs = Battlelog.query.filter_by(deck_id=deck_id).all()

        # Calculate average turns first and ensure it's a float
        avg_turns_data = self._calculate_avg_turns(deck_logs)
        if isinstance(avg_turns_data, (int, float)):
            average_turns = float(avg_turns_data)
        else:
            average_turns = float(avg_turns_data['average'])

        # Prepare analysis with type-safe values
        analysis = {
            'deck_id': deck_id,
            'timestamp': datetime.now(timezone.utc),
            'win_rate': float(self._calculate_win_rate(deck_logs)),
            'total_battles': len(deck_logs),
            'average_turns': average_turns,  # Now guaranteed to be a float
            'performance_metrics': self._identify_key_cards(deck_logs),
            'trend_analysis': self._analyze_performance_trend(deck_logs)
        }

        ai_analysis = AIAnalysis(**analysis)
        db.session.add(ai_analysis)
        db.session.commit()

        return analysis
    def _calculate_win_rate(self, logs):
        """Calculate win rate with statistical confidence"""
        if not logs:
            return 0.0
        wins = sum(1 for log in logs if log.win_loss)
        return (wins / len(logs)) * 100

    def _calculate_avg_turns(self, logs):
        """Calculate average turns with trend analysis"""
        if not logs:
            return 0
        turns = [log.total_turns for log in logs]
        return {
            'average': np.mean(turns),
            'median': np.median(turns),
            'trend': 'increasing' if np.polyfit(range(len(turns)), turns, 1)[0] > 0 else 'decreasing'
        }

    def _identify_key_cards(self, logs):
        """Analyze card effectiveness using frequency and win correlation"""
        card_stats = {}
        for log in logs:
            for card in log.most_used_cards:
                if card not in card_stats:
                    card_stats[card] = {'uses': 0, 'wins': 0}
                card_stats[card]['uses'] += 1
                if log.win_loss:
                    card_stats[card]['wins'] += 1
        
        return {
            'most_effective': sorted(
                card_stats.items(),
                key=lambda x: x[1]['wins'] / x[1]['uses'] if x[1]['uses'] > 0 else 0,
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
        """Identify opponent's deck strategy based on card patterns"""
        # Default strategies based on card combinations
        strategies = {
            'aggro': {'ai', 'direct_damage'},
            'control': {'energy_denial', 'status_effects'},
            'combo': {'search_cards', 'energy_acceleration'},
            'stall': {'healing', 'damage_reduction'}
        }
        
        opponent_cards = set(log.opponent_cards)
        
        # Determine strategy based on most matching card patterns
        strategy_scores = {
            name: len(pattern & opponent_cards)
            for name, pattern in strategies.items()
        }
        
        # Return the strategy with highest score, default to 'unknown'
        return max(strategy_scores.items(), 
                  key=lambda x: x[1])[0] if strategy_scores else 'unknown'
    def _identify_weak_performers(self, card_performance):
        """Identify cards with poor performance metrics"""
        weak_performers = []
        
        for card_stats in card_performance['most_used']:
            card_name, stats = card_stats
            # Consider a card weak if used frequently but has < 40% win rate
            if stats['uses'] >= 5 and (stats['wins'] / stats['uses']) < 0.4:
                weak_performers.append(card_name)
                
        return weak_performers
    
    def _generate_suggestions(self, logs, deck):
        """Generate deck improvement suggestions based on performance data"""
        suggestions = {
            'card_recommendations': [],
            'strategy_tips': [],
            'sideboard_suggestions': []
        }

        card_performance = self._identify_key_cards(logs)
        weak_cards = self._identify_weak_performers(card_performance)

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

     

    def _analyze_performance_trend(self, logs):
        """Analyze performance trends over time"""
        if not logs:
            return {
                'trend': 'insufficient_data',
                'consistency_score': 0.0,
                'last_10_games_wr': 0.0
            }
                
        # Calculate win rates for each window
        win_rates = []
        for i in range(len(logs)):
            window = logs[max(0, i-9):i+1]  # Get up to 10 most recent games
            wins = sum(1 for log in window if log.win_loss)
            win_rates.append(wins / len(window))

        # Calculate trend and consistency metrics
        trend = 'improving' if len(win_rates) > 1 and win_rates[-1] > win_rates[0] else 'stable'
        consistency = float(np.std(win_rates)) if win_rates else 0.0
        recent_wr = win_rates[-1] if win_rates else 0.0

        return {
            'trend': trend,
            'consistency_score': consistency,
            'last_10_games_wr': recent_wr
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

