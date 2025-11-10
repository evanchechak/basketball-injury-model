"""
Quick Start Script - Analyze Today's Injury Impact

This script provides a simple interface to analyze betting opportunities
when you hear about an injury.
"""

from injury_impact_model import InjuryImpactModel
from data_collector import NBADataCollector
import pandas as pd


def quick_analysis(injured_player_name, team_abbrev, betting_lines_dict):
    """
    Quick analysis when a player is injured
    
    Parameters:
    - injured_player_name: e.g., "Joel Embiid"
    - team_abbrev: e.g., "PHI"
    - betting_lines_dict: e.g., {'Tyrese Maxey': 25.5, 'Tobias Harris': 17.5}
    """
    
    print(f"\n{'='*80}")
    print(f"QUICK ANALYSIS: {injured_player_name} OUT")
    print(f"{'='*80}\n")
    
    collector = NBADataCollector()
    
    # Get team ID
    team_id = collector.get_team_id_from_abbrev(team_abbrev)
    if not team_id:
        print(f"Error: Team '{team_abbrev}' not found")
        return
    
    print(f"Loading data for {team_abbrev}...")
    
    # Search for injured player
    player_results = collector.search_player(injured_player_name)
    if not player_results:
        print(f"Error: Player '{injured_player_name}' not found")
        return
    
    injured_player = player_results[0]
    injured_player_id = injured_player['PERSON_ID']
    print(f"Found: {injured_player['DISPLAY_FIRST_LAST']}")
    
    # Get roster
    print(f"Fetching {team_abbrev} roster...")
    roster = collector.fetch_team_roster(team_id)
    
    if len(roster) == 0:
        print("Error: Could not fetch roster")
        return
    
    # Collect game logs
    print("Collecting game logs (this may take a minute)...")
    all_game_logs = []
    
    for _, player in roster.iterrows():
        player_id = player['PLAYER_ID']
        game_logs = collector.fetch_player_game_logs(player_id)
        if len(game_logs) > 0:
            all_game_logs.append(game_logs)
        
        # Small delay to avoid rate limiting
        import time
        time.sleep(0.6)
    
    if not all_game_logs:
        print("Error: Could not collect game logs")
        return
    
    # Combine game logs
    player_stats = pd.concat(all_game_logs, ignore_index=True)
    games = player_stats[['GAME_ID', 'GAME_DATE', 'MATCHUP']].drop_duplicates()
    
    print(f"Loaded {len(player_stats)} player performances from {len(games)} games")
    
    # Initialize model
    model = InjuryImpactModel()
    model.load_data(games, player_stats)
    
    # Find opportunities
    opportunities = model.find_betting_opportunities(
        injured_player_id=injured_player_id,
        injured_player_name=injured_player_name,
        team_id=team_id,
        betting_lines=betting_lines_dict,
        stat='PTS',
        min_edge=0.03  # 3% minimum edge
    )
    
    # Display results
    if len(opportunities) > 0:
        print("\n" + "="*80)
        print("RECOMMENDED BETS:")
        print("="*80)
        
        for _, opp in opportunities.iterrows():
            print(f"\n{opp['Player']}: {opp['Recommendation']} {opp['Betting Line']}")
            print(f"  Prediction: {opp['Prediction']:.1f} points")
            print(f"  Edge: +{opp['Edge %']:.2f}%")
            print(f"  Confidence: {opp['Confidence %']:.1f}%")
            print(f"  Historical Avg w/o {injured_player_name}: {opp['Historical w/o Star']:.1f}")
            print(f"  Sample Size: {int(opp['Sample Size'])} games")
        
        # Kelly Criterion recommendations
        print("\n" + "="*80)
        print("BET SIZING (Kelly Criterion)")
        print("="*80)
        print("\nWith $1,000 bankroll:")
        
        for _, opp in opportunities.iterrows():
            prob_win = opp['Confidence %'] / 100
            odds = 0.909
            kelly = (odds * prob_win - (1 - prob_win)) / odds
            conservative = kelly * 0.25
            
            print(f"\n{opp['Player']} {opp['Recommendation']} {opp['Betting Line']}:")
            print(f"  Full Kelly: ${kelly * 1000:.2f} ({kelly*100:.1f}% of bankroll)")
            print(f"  Conservative: ${conservative * 1000:.2f} ({conservative*100:.1f}% of bankroll)")
    else:
        print("\nNo profitable opportunities found at current lines.")
    
    return opportunities


if __name__ == "__main__":
    # Example usage
    print("\nWelcome to NBA Injury Impact Analyzer!")
    print("="*80)
    
    # Example 1: Joel Embiid out
    print("\nEXAMPLE: Analyzing when Joel Embiid is OUT")
    
    # Get today's betting lines from your sportsbook
    betting_lines = {
        'Tyrese Maxey': 25.5,
        'Tobias Harris': 17.5,
        "De'Anthony Melton": 12.5,
        'Kelly Oubre Jr.': 15.5
    }
    
    # Run analysis
    opportunities = quick_analysis(
        injured_player_name="Joel Embiid",
        team_abbrev="PHI",
        betting_lines_dict=betting_lines
    )
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("""
To use with other teams/players, modify the script:

opportunities = quick_analysis(
    injured_player_name="Luka Doncic",  # Change player name
    team_abbrev="DAL",                   # Change team
    betting_lines_dict={                 # Update lines from sportsbook
        'Kyrie Irving': 23.5,
        'Tim Hardaway Jr.': 14.5
    }
)
    """)
