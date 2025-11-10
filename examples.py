"""
Example Usage: NBA Injury Impact Betting Model

This script demonstrates how to use the betting model with example data
"""

import pandas as pd
import numpy as np
from injury_impact_model import InjuryImpactModel
from data_collector import NBADataCollector


def generate_sample_data():
    """
    Generate sample data for demonstration purposes
    This simulates 76ers data with Joel Embiid and teammates
    """
    
    # Player IDs (using realistic IDs)
    EMBIID_ID = 203954
    MAXEY_ID = 1630178
    HARRIS_ID = 202699
    MELTON_ID = 1629001
    OUBRE_ID = 1626162
    
    # Generate games for the season
    dates = pd.date_range('2024-10-25', periods=40, freq='2D')
    
    # Create game data
    games = []
    player_stats = []
    game_id = 20240001
    
    for date in dates:
        # Embiid sits out ~40% of games (load management)
        embiid_plays = np.random.random() > 0.4
        
        games.append({
            'GAME_ID': game_id,
            'GAME_DATE': date,
            'MATCHUP': 'PHI vs. BOS' if np.random.random() > 0.5 else 'PHI @ BOS',
            'TEAM_ID': 1610612755
        })
        
        # Joel Embiid stats (when he plays)
        if embiid_plays:
            player_stats.append({
                'GAME_ID': game_id,
                'GAME_DATE': date,
                'PLAYER_ID': EMBIID_ID,
                'PLAYER_NAME': 'Joel Embiid',
                'TEAM_ID': 1610612755,
                'MATCHUP': games[-1]['MATCHUP'],
                'MIN': np.random.uniform(30, 37),
                'PTS': np.random.normal(28, 5),  # Avg 28 ppg
                'REB': np.random.normal(11, 2),
                'AST': np.random.normal(5, 2),
                'FG_PCT': np.random.uniform(0.45, 0.58)
            })
        
        # Tyrese Maxey (benefits when Embiid is out)
        if embiid_plays:
            maxey_pts = np.random.normal(24, 4)  # 24 ppg with Embiid
        else:
            maxey_pts = np.random.normal(30, 5)  # 30 ppg without Embiid
        
        player_stats.append({
            'GAME_ID': game_id,
            'GAME_DATE': date,
            'PLAYER_ID': MAXEY_ID,
            'PLAYER_NAME': 'Tyrese Maxey',
            'TEAM_ID': 1610612755,
            'MATCHUP': games[-1]['MATCHUP'],
            'MIN': np.random.uniform(34, 38),
            'PTS': maxey_pts,
            'REB': np.random.normal(4, 1.5),
            'AST': np.random.normal(6, 2),
            'FG_PCT': np.random.uniform(0.42, 0.52)
        })
        
        # Tobias Harris (slight benefit when Embiid is out)
        if embiid_plays:
            harris_pts = np.random.normal(16, 3)
        else:
            harris_pts = np.random.normal(19, 4)
        
        player_stats.append({
            'GAME_ID': game_id,
            'GAME_DATE': date,
            'PLAYER_ID': HARRIS_ID,
            'PLAYER_NAME': 'Tobias Harris',
            'TEAM_ID': 1610612755,
            'MATCHUP': games[-1]['MATCHUP'],
            'MIN': np.random.uniform(30, 35),
            'PTS': harris_pts,
            'REB': np.random.normal(6, 2),
            'AST': np.random.normal(3, 1),
            'FG_PCT': np.random.uniform(0.43, 0.51)
        })
        
        # De'Anthony Melton (moderate benefit)
        if embiid_plays:
            melton_pts = np.random.normal(11, 3)
        else:
            melton_pts = np.random.normal(14, 3.5)
        
        player_stats.append({
            'GAME_ID': game_id,
            'GAME_DATE': date,
            'PLAYER_ID': MELTON_ID,
            'PLAYER_NAME': "De'Anthony Melton",
            'TEAM_ID': 1610612755,
            'MATCHUP': games[-1]['MATCHUP'],
            'MIN': np.random.uniform(25, 32),
            'PTS': melton_pts,
            'REB': np.random.normal(4, 1.5),
            'AST': np.random.normal(3, 1.5),
            'FG_PCT': np.random.uniform(0.39, 0.48)
        })
        
        # Kelly Oubre Jr (slight benefit)
        if embiid_plays:
            oubre_pts = np.random.normal(14, 3)
        else:
            oubre_pts = np.random.normal(16, 3.5)
        
        player_stats.append({
            'GAME_ID': game_id,
            'GAME_DATE': date,
            'PLAYER_ID': OUBRE_ID,
            'PLAYER_NAME': 'Kelly Oubre Jr.',
            'TEAM_ID': 1610612755,
            'MATCHUP': games[-1]['MATCHUP'],
            'MIN': np.random.uniform(28, 34),
            'PTS': oubre_pts,
            'REB': np.random.normal(5, 1.5),
            'AST': np.random.normal(1.5, 1),
            'FG_PCT': np.random.uniform(0.41, 0.50)
        })
        
        game_id += 1
    
    games_df = pd.DataFrame(games)
    player_stats_df = pd.DataFrame(player_stats)
    
    return games_df, player_stats_df, EMBIID_ID


def example_1_basic_impact_analysis():
    """
    Example 1: Basic impact analysis when Embiid is out
    """
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Impact Analysis")
    print("="*80)
    
    # Generate sample data
    games_df, player_stats_df, embiid_id = generate_sample_data()
    
    # Initialize model
    model = InjuryImpactModel()
    model.load_data(games_df, player_stats_df)
    
    # Analyze impact on teammates
    print("\nAnalyzing impact of Joel Embiid's absence on teammates...")
    impacts = model.analyze_injury_impact(
        injured_player_id=embiid_id,
        team_id=1610612755,
        stat='PTS',
        top_n=5
    )
    
    print("\n" + "-"*80)
    print("Top Affected Players:")
    print("-"*80)
    print(impacts[['player_name', 'with_star_avg', 'without_star_avg', 
                   'difference', 'percent_change', 'without_star_count']].to_string(index=False))
    

def example_2_betting_opportunities():
    """
    Example 2: Find betting opportunities with actual betting lines
    """
    print("\n" + "="*80)
    print("EXAMPLE 2: Finding Betting Opportunities")
    print("="*80)
    
    # Generate sample data
    games_df, player_stats_df, embiid_id = generate_sample_data()
    
    # Initialize model
    model = InjuryImpactModel()
    model.load_data(games_df, player_stats_df)
    
    # Simulate betting lines (these would come from a sportsbook)
    betting_lines = {
        'Tyrese Maxey': 25.5,      # His line is lower than expected
        'Tobias Harris': 17.5,
        "De'Anthony Melton": 12.5,
        'Kelly Oubre Jr.': 15.5
    }
    
    print("\nBetting Lines (Player Points Over/Under):")
    for player, line in betting_lines.items():
        print(f"  {player}: {line}")
    
    # Find opportunities
    opportunities = model.find_betting_opportunities(
        injured_player_id=embiid_id,
        injured_player_name='Joel Embiid',
        team_id=1610612755,
        betting_lines=betting_lines,
        stat='PTS',
        min_edge=0.03  # Require 3% edge
    )
    
    if len(opportunities) > 0:
        print("\n" + "="*80)
        print("RECOMMENDED BETS:")
        print("="*80)
        print(opportunities.to_string(index=False))
        
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        for _, opp in opportunities.iterrows():
            print(f"\n{opp['Player']} - {opp['Recommendation']} {opp['Betting Line']}")
            print(f"  Expected Value: +{opp['Edge %']:.2f}%")
            print(f"  Confidence: {opp['Confidence %']:.1f}%")
            print(f"  Historical Difference: +{opp['Difference']:.1f} points without Embiid")
    

def example_3_compare_multiple_scenarios():
    """
    Example 3: Compare impact of different star players being out
    """
    print("\n" + "="*80)
    print("EXAMPLE 3: Comparing Multiple Star Absences")
    print("="*80)
    
    # Generate sample data
    games_df, player_stats_df, embiid_id = generate_sample_data()
    
    # Initialize model
    model = InjuryImpactModel()
    model.load_data(games_df, player_stats_df)
    
    # Analyze Maxey specifically
    maxey_id = 1630178
    
    maxey_impact = model.measure_teammate_impact(
        star_player_id=embiid_id,
        teammate_id=maxey_id,
        stat='PTS'
    )
    
    if maxey_impact:
        print("\nTyrese Maxey's Performance:")
        print("-"*80)
        print(f"With Embiid:    {maxey_impact['with_star_avg']:.1f} PPG "
              f"({maxey_impact['with_star_count']} games)")
        print(f"Without Embiid: {maxey_impact['without_star_avg']:.1f} PPG "
              f"({maxey_impact['without_star_count']} games)")
        print(f"Difference:     +{maxey_impact['difference']:.1f} PPG "
              f"({maxey_impact['percent_change']:.1f}% increase)")
        
        if maxey_impact['p_value']:
            print(f"Statistical Significance: p={maxey_impact['p_value']:.4f} "
                  f"({'Significant' if maxey_impact['significant'] else 'Not Significant'})")


def example_4_kelly_criterion_sizing():
    """
    Example 4: Calculate optimal bet sizing using Kelly Criterion
    """
    print("\n" + "="*80)
    print("EXAMPLE 4: Optimal Bet Sizing with Kelly Criterion")
    print("="*80)
    
    # Generate sample data
    games_df, player_stats_df, embiid_id = generate_sample_data()
    
    # Initialize model
    model = InjuryImpactModel()
    model.load_data(games_df, player_stats_df)
    
    # Sample betting opportunity
    betting_lines = {'Tyrese Maxey': 25.5}
    
    opportunities = model.find_betting_opportunities(
        injured_player_id=embiid_id,
        injured_player_name='Joel Embiid',
        team_id=1610612755,
        betting_lines=betting_lines,
        stat='PTS'
    )
    
    if len(opportunities) > 0:
        opp = opportunities.iloc[0]
        
        # Kelly Criterion: f = (bp - q) / b
        # where f = fraction of bankroll to bet
        #       b = odds received (0.909 for -110)
        #       p = probability of winning
        #       q = probability of losing (1-p)
        
        prob_win = opp['Confidence %'] / 100
        prob_lose = 1 - prob_win
        odds = 0.909  # -110 odds
        
        kelly_fraction = (odds * prob_win - prob_lose) / odds
        kelly_fraction = max(0, kelly_fraction)  # Can't be negative
        
        # Conservative Kelly (typically use 25-50% of full Kelly)
        conservative_kelly = kelly_fraction * 0.25
        
        print(f"\nBetting Opportunity: {opp['Player']} {opp['Recommendation']} {opp['Betting Line']}")
        print(f"Win Probability: {prob_win:.2%}")
        print(f"Expected Value: +{opp['Edge %']:.2f}%")
        print(f"\nBankroll Allocation:")
        print(f"  Full Kelly: {kelly_fraction:.2%} of bankroll")
        print(f"  Conservative (25%): {conservative_kelly:.2%} of bankroll")
        print(f"\nExample with $1,000 bankroll:")
        print(f"  Full Kelly bet: ${kelly_fraction * 1000:.2f}")
        print(f"  Conservative bet: ${conservative_kelly * 1000:.2f}")


def run_all_examples():
    """Run all example scenarios"""
    example_1_basic_impact_analysis()
    example_2_betting_opportunities()
    example_3_compare_multiple_scenarios()
    example_4_kelly_criterion_sizing()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    # Run all examples
    run_all_examples()
    
    print("\n" + "="*80)
    print("NEXT STEPS:")
    print("="*80)
    print("""
1. Collect real NBA data:
   - Use data_collector.py to fetch current season data
   - Or load your own CSV files with game logs

2. Update betting lines:
   - Get current lines from sportsbooks (DraftKings, FanDuel, etc.)
   - Update the betting_lines dictionary

3. Run analysis when injuries are announced:
   - Check NBA injury reports daily
   - Run the model for affected teams
   - Place bets where there's positive expected value

4. Track results:
   - Keep a log of all bets placed
   - Calculate actual ROI over time
   - Adjust edge thresholds based on performance

5. Advanced features to add:
   - Opponent defensive ratings
   - Home/away splits
   - Back-to-back games
   - Recent form (last 5 games)
   - Historical head-to-head matchups
    """)
