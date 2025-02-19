import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from flask import Blueprint, jsonify
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
    
    def analyze_deck(self, deck_id):
        """Perform comprehensive deck analysis"""
        if not self.is_trained:
            self.train_on_all_logs()
            
        deck = Deck.query.get(deck_id)
        deck_logs = Battlelog.query.filter_by(deck_id=deck_id).all()
        
        analysis = {
            'deck_id': deck_id,
            'name': deck.name,
            'total_battles': len(deck_logs),
            'win_rate': self._calculate_win_rate(deck_logs),
            'performance_metrics': {
                'average_turns': self._calculate_avg_turns(deck_logs),
                'common_winning_cards': self._identify_key_cards(deck_logs),
                'matchup_analysis': self._analyze_matchups(deck_logs),
                'suggested_improvements': self._generate_suggestions(deck_logs, deck)
            },
            'trend_analysis': self._analyze_performance_trend(deck_logs),
            'timestamp': datetime.utcnow()
        }
        
        ai_analysis = AIAnalysis(
            deck_id=deck_id,
            **analysis
        )
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

    def _analyze_performance_trend(self, logs):
        """Analyze performance trends over time"""
        if not logs:
            return {'trend': 'insufficient_data'}
            
        sorted_logs = sorted(logs, key=lambda x: x.timestamp)
        window_size = min(10, len(logs))
        rolling_wr = []
        
        for i in range(len(sorted_logs) - window_size + 1):
            window = sorted_logs[i:i + window_size]
            wr = sum(1 for log in window if log.win_loss) / window_size
            rolling_wr.append(wr)
            
        return {
            'recent_trend': 'improving' if len(rolling_wr) > 1 and rolling_wr[-1] > rolling_wr[0] else 'declining',
            'consistency_score': np.std(rolling_wr),
            'last_10_games_wr': rolling_wr[-1] if rolling_wr else 0
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
