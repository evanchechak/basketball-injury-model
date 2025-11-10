"""
NBA Injury Impact Betting Model
Analyzes how player absences affect teammate performance and identifies betting opportunities
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class InjuryImpactModel:
    def __init__(self):
        self.player_baselines = {}
        self.injury_impacts = {}
        self.models = {}
        
    def load_data(self, games_df, player_stats_df, injury_reports_df=None):
        """
        Load game and player statistics data
        
        Parameters:
        - games_df: DataFrame with game information
        - player_stats_df: DataFrame with player box scores
        - injury_reports_df: Optional DataFrame with injury information
        """
        self.games = games_df
        self.player_stats = player_stats_df
        self.injury_reports = injury_reports_df
        
        print(f"Loaded {len(games_df)} games and {len(player_stats_df)} player performances")
        
    def calculate_baseline(self, player_id, stat='PTS', last_n_games=15):
        """Calculate player's baseline performance"""
        player_games = self.player_stats[
            self.player_stats['PLAYER_ID'] == player_id
        ].sort_values('GAME_DATE', ascending=False)
        
        if len(player_games) == 0:
            return None
            
        recent_games = player_games.head(last_n_games)
        
        baseline = {
            'mean': recent_games[stat].mean(),
            'median': recent_games[stat].median(),
            'std': recent_games[stat].std(),
            'sample_size': len(recent_games)
        }
        
        return baseline
    
    def measure_teammate_impact(self, star_player_id, teammate_id, stat='PTS', min_games=5):
        """
        Measure how teammate performs when star player is out
        
        Returns impact metrics including averages with/without star and statistical significance
        """
        # Get teammate's games
        teammate_games = self.player_stats[
            self.player_stats['PLAYER_ID'] == teammate_id
        ].copy()
        
        if len(teammate_games) == 0:
            return None
        
        # Get star player's games (games they actually played)
        star_games = self.player_stats[
            self.player_stats['PLAYER_ID'] == star_player_id
        ]['GAME_ID'].unique()
        
        # Split teammate games
        with_star = teammate_games[teammate_games['GAME_ID'].isin(star_games)]
        without_star = teammate_games[~teammate_games['GAME_ID'].isin(star_games)]
        
        if len(without_star) < min_games:
            return None
        
        # Calculate statistics
        with_star_avg = with_star[stat].mean()
        without_star_avg = without_star[stat].mean()
        difference = without_star_avg - with_star_avg
        
        # Statistical test
        if len(with_star) > 0 and len(without_star) > 0:
            t_stat, p_value = stats.ttest_ind(without_star[stat], with_star[stat])
        else:
            t_stat, p_value = None, None
        
        impact = {
            'with_star_avg': with_star_avg,
            'without_star_avg': without_star_avg,
            'difference': difference,
            'percent_change': (difference / with_star_avg * 100) if with_star_avg > 0 else 0,
            'with_star_count': len(with_star),
            'without_star_count': len(without_star),
            'p_value': p_value,
            'significant': p_value < 0.05 if p_value else False,
            'with_star_std': with_star[stat].std(),
            'without_star_std': without_star[stat].std()
        }
        
        return impact
    
    def build_prediction_model(self, player_id, stat='PTS'):
        """
        Build a machine learning model to predict player performance
        """
        player_data = self.player_stats[
            self.player_stats['PLAYER_ID'] == player_id
        ].copy()
        
        if len(player_data) < 20:
            return None
        
        # Feature engineering
        player_data['HOME'] = (player_data['MATCHUP'].str.contains('vs.')).astype(int)
        player_data['ROLLING_AVG_5'] = player_data[stat].rolling(5, min_periods=1).mean()
        player_data['ROLLING_STD_5'] = player_data[stat].rolling(5, min_periods=1).std()
        
        # Prepare features
        feature_cols = ['MIN', 'HOME', 'ROLLING_AVG_5']
        player_data = player_data.dropna(subset=feature_cols + [stat])
        
        if len(player_data) < 10:
            return None
        
        X = player_data[feature_cols]
        y = player_data[stat]
        
        # Use Random Forest for better predictions
        model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
        model.fit(X, y)
        
        return {
            'model': model,
            'features': feature_cols,
            'mean_error': np.abs(y - model.predict(X)).mean()
        }
    
    def predict_performance(self, player_id, stat='PTS', is_home=True, expected_minutes=30):
        """
        Predict player performance for upcoming game
        """
        player_data = self.player_stats[
            self.player_stats['PLAYER_ID'] == player_id
        ].copy()
        
        if len(player_data) < 10:
            # Fall back to simple average
            return player_data[stat].mean() if len(player_data) > 0 else None
        
        # Calculate rolling average
        rolling_avg = player_data[stat].tail(5).mean()
        rolling_std = player_data[stat].tail(5).std()
        
        # Build model if not exists
        if player_id not in self.models:
            model_data = self.build_prediction_model(player_id, stat)
            if model_data:
                self.models[player_id] = model_data
        
        # Make prediction
        if player_id in self.models:
            model_info = self.models[player_id]
            features = pd.DataFrame({
                'MIN': [expected_minutes],
                'HOME': [1 if is_home else 0],
                'ROLLING_AVG_5': [rolling_avg]
            })
            prediction = model_info['model'].predict(features)[0]
        else:
            prediction = rolling_avg
        
        return {
            'prediction': prediction,
            'std': rolling_std,
            'confidence_interval_low': prediction - 1.96 * rolling_std,
            'confidence_interval_high': prediction + 1.96 * rolling_std
        }
    
    def calculate_betting_edge(self, prediction, betting_line, std_dev):
        """
        Calculate expected value and probability of going over the line
        """
        if std_dev == 0 or np.isnan(std_dev):
            std_dev = prediction * 0.15  # Assume 15% coefficient of variation
        
        # Probability of going over
        z_score = (betting_line - prediction) / std_dev
        prob_over = 1 - stats.norm.cdf(z_score)
        prob_under = stats.norm.cdf(z_score)
        
        # Calculate expected value (assuming -110 odds on both sides)
        # Need 52.4% win rate to break even at -110
        over_ev = (prob_over * 0.909) - (1 - prob_over)
        under_ev = (prob_under * 0.909) - (1 - prob_under)
        
        result = {
            'prediction': prediction,
            'line': betting_line,
            'prob_over': prob_over,
            'prob_under': prob_under,
            'over_ev': over_ev,
            'under_ev': under_ev,
            'std_dev': std_dev
        }
        
        # Determine recommendation (require at least 5% edge)
        if over_ev > 0.05:
            result['recommendation'] = 'OVER'
            result['edge'] = over_ev
            result['confidence'] = prob_over
        elif under_ev > 0.05:
            result['recommendation'] = 'UNDER'
            result['edge'] = under_ev
            result['confidence'] = prob_under
        else:
            result['recommendation'] = 'NO BET'
            result['edge'] = max(over_ev, under_ev)
            result['confidence'] = max(prob_over, prob_under)
        
        return result
    
    def analyze_injury_impact(self, injured_player_id, team_id, stat='PTS', top_n=5):
        """
        Analyze which teammates are most affected by a player's absence
        """
        # Get all teammates
        team_games = self.player_stats[
            self.player_stats['TEAM_ID'] == team_id
        ]
        
        teammates = team_games['PLAYER_ID'].unique()
        teammates = [t for t in teammates if t != injured_player_id]
        
        impacts = []
        
        for teammate_id in teammates:
            impact = self.measure_teammate_impact(
                injured_player_id, 
                teammate_id, 
                stat,
                min_games=3
            )
            
            if impact and impact['difference'] > 1:  # At least 1 point difference
                teammate_name = team_games[
                    team_games['PLAYER_ID'] == teammate_id
                ]['PLAYER_NAME'].iloc[0]
                
                impacts.append({
                    'player_id': teammate_id,
                    'player_name': teammate_name,
                    **impact
                })
        
        # Sort by absolute difference
        impacts_df = pd.DataFrame(impacts)
        if len(impacts_df) > 0:
            impacts_df = impacts_df.sort_values('difference', ascending=False)
            return impacts_df.head(top_n)
        
        return pd.DataFrame()
    
    def find_betting_opportunities(self, injured_player_id, injured_player_name, 
                                   team_id, betting_lines, stat='PTS', 
                                   min_edge=0.05):
        """
        Find betting opportunities when a star player is injured
        
        Parameters:
        - injured_player_id: Player ID of injured star
        - injured_player_name: Name of injured player
        - team_id: Team ID
        - betting_lines: Dict of {player_id: betting_line} or {player_name: betting_line}
        - stat: Stat to analyze (default: PTS)
        - min_edge: Minimum edge required (default: 5%)
        
        Returns DataFrame of betting opportunities
        """
        print(f"\n{'='*80}")
        print(f"ANALYZING IMPACT: {injured_player_name} OUT")
        print(f"{'='*80}\n")
        
        # Analyze teammate impacts
        impacts = self.analyze_injury_impact(injured_player_id, team_id, stat)
        
        if len(impacts) == 0:
            print("No significant impacts found")
            return pd.DataFrame()
        
        opportunities = []
        
        print(f"Top Affected Teammates:")
        print(f"{'-'*80}")
        
        for _, player_impact in impacts.iterrows():
            player_id = player_impact['player_id']
            player_name = player_impact['player_name']
            
            # Get betting line (check both by ID and name)
            betting_line = None
            if player_id in betting_lines:
                betting_line = betting_lines[player_id]
            elif player_name in betting_lines:
                betting_line = betting_lines[player_name]
            
            if betting_line is None:
                print(f"  {player_name}: +{player_impact['difference']:.1f} {stat} "
                      f"(No betting line available)")
                continue
            
            # Predict performance without injured player
            baseline = self.calculate_baseline(player_id, stat)
            if not baseline:
                continue
            
            # Use the "without star" average as prediction
            prediction = player_impact['without_star_avg']
            std_dev = player_impact['without_star_std']
            
            # Calculate betting edge
            bet_analysis = self.calculate_betting_edge(prediction, betting_line, std_dev)
            
            if bet_analysis['edge'] >= min_edge:
                opportunities.append({
                    'Player': player_name,
                    'Stat': stat,
                    'Prediction': prediction,
                    'Betting Line': betting_line,
                    'Recommendation': bet_analysis['recommendation'],
                    'Edge %': bet_analysis['edge'] * 100,
                    'Confidence %': bet_analysis['confidence'] * 100,
                    'Historical w/ Star': player_impact['with_star_avg'],
                    'Historical w/o Star': player_impact['without_star_avg'],
                    'Difference': player_impact['difference'],
                    'Sample Size': player_impact['without_star_count']
                })
                
                print(f"  ✓ {player_name}:")
                print(f"      Avg with {injured_player_name}: {player_impact['with_star_avg']:.1f}")
                print(f"      Avg without {injured_player_name}: {player_impact['without_star_avg']:.1f}")
                print(f"      Difference: +{player_impact['difference']:.1f}")
                print(f"      Betting Line: {betting_line}")
                print(f"      Prediction: {prediction:.1f}")
                print(f"      → {bet_analysis['recommendation']} (Edge: {bet_analysis['edge']*100:.1f}%)")
            else:
                print(f"  {player_name}: +{player_impact['difference']:.1f} {stat} "
                      f"(Line: {betting_line}, Edge: {bet_analysis['edge']*100:.1f}% - Below threshold)")
        
        if len(opportunities) > 0:
            print(f"\n{'='*80}")
            print(f"BETTING OPPORTUNITIES FOUND: {len(opportunities)}")
            print(f"{'='*80}\n")
            return pd.DataFrame(opportunities).sort_values('Edge %', ascending=False)
        else:
            print(f"\n{'='*80}")
            print("NO PROFITABLE OPPORTUNITIES FOUND")
            print(f"{'='*80}\n")
            return pd.DataFrame()
