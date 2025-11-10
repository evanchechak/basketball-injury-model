"""
NBA Data Collection Module
Fetches player stats and game data from NBA Stats API
"""

import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import json


class NBADataCollector:
    def __init__(self):
        self.base_url = "https://stats.nba.com/stats"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://stats.nba.com/',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
    def get_current_season(self):
        """Get current NBA season string (e.g., '2024-25')"""
        now = datetime.now()
        if now.month >= 10:  # Season starts in October
            return f"{now.year}-{str(now.year + 1)[-2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[-2:]}"
    
    def fetch_player_game_logs(self, player_id, season=None):
        """
        Fetch game logs for a specific player
        """
        if season is None:
            season = self.get_current_season()
        
        url = f"{self.base_url}/playergamelog"
        params = {
            'PlayerID': player_id,
            'Season': season,
            'SeasonType': 'Regular Season'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if 'resultSets' in data and len(data['resultSets']) > 0:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']
                df = pd.DataFrame(rows, columns=headers)
                return df
            
        except Exception as e:
            print(f"Error fetching game logs for player {player_id}: {e}")
        
        return pd.DataFrame()
    
    def fetch_team_roster(self, team_id, season=None):
        """
        Fetch current roster for a team
        """
        if season is None:
            season = self.get_current_season()
        
        url = f"{self.base_url}/commonteamroster"
        params = {
            'TeamID': team_id,
            'Season': season
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if 'resultSets' in data and len(data['resultSets']) > 0:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']
                df = pd.DataFrame(rows, columns=headers)
                return df
            
        except Exception as e:
            print(f"Error fetching roster for team {team_id}: {e}")
        
        return pd.DataFrame()
    
    def fetch_league_game_log(self, season=None, player_or_team='P'):
        """
        Fetch game logs for all players in the league
        This is a large dataset - use sparingly
        """
        if season is None:
            season = self.get_current_season()
        
        url = f"{self.base_url}/leaguegamelog"
        params = {
            'Season': season,
            'SeasonType': 'Regular Season',
            'PlayerOrTeam': player_or_team,
            'Counter': '0',
            'Sorter': 'DATE',
            'Direction': 'DESC'
        }
        
        try:
            print(f"Fetching league game logs for {season}... (this may take a moment)")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            data = response.json()
            
            if 'resultSets' in data and len(data['resultSets']) > 0:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']
                df = pd.DataFrame(rows, columns=headers)
                print(f"Fetched {len(df)} game logs")
                return df
            
        except Exception as e:
            print(f"Error fetching league game logs: {e}")
        
        return pd.DataFrame()
    
    def search_player(self, player_name):
        """
        Search for a player by name and return their ID
        """
        url = f"{self.base_url}/commonallplayers"
        params = {
            'LeagueID': '00',
            'Season': self.get_current_season(),
            'IsOnlyCurrentSeason': '1'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            data = response.json()
            
            if 'resultSets' in data and len(data['resultSets']) > 0:
                headers = data['resultSets'][0]['headers']
                rows = data['resultSets'][0]['rowSet']
                df = pd.DataFrame(rows, columns=headers)
                
                # Search for player
                matches = df[df['DISPLAY_FIRST_LAST'].str.contains(player_name, case=False)]
                
                if len(matches) > 0:
                    return matches[['PERSON_ID', 'DISPLAY_FIRST_LAST', 'TEAM_ID']].to_dict('records')
                
        except Exception as e:
            print(f"Error searching for player: {e}")
        
        return []
    
    def get_team_id_from_abbrev(self, team_abbrev):
        """
        Get team ID from abbreviation (e.g., 'PHI' -> 1610612755)
        """
        team_mapping = {
            'ATL': 1610612737, 'BOS': 1610612738, 'BKN': 1610612751, 'CHA': 1610612766,
            'CHI': 1610612741, 'CLE': 1610612739, 'DAL': 1610612742, 'DEN': 1610612743,
            'DET': 1610612765, 'GSW': 1610612744, 'HOU': 1610612745, 'IND': 1610612754,
            'LAC': 1610612746, 'LAL': 1610612747, 'MEM': 1610612763, 'MIA': 1610612748,
            'MIL': 1610612749, 'MIN': 1610612750, 'NOP': 1610612740, 'NYK': 1610612752,
            'OKC': 1610612760, 'ORL': 1610612753, 'PHI': 1610612755, 'PHX': 1610612756,
            'POR': 1610612757, 'SAC': 1610612758, 'SAS': 1610612759, 'TOR': 1610612761,
            'UTA': 1610612762, 'WAS': 1610612764
        }
        return team_mapping.get(team_abbrev.upper())
    
    def save_data(self, df, filename):
        """Save DataFrame to CSV"""
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    
    def load_data(self, filename):
        """Load DataFrame from CSV"""
        try:
            df = pd.read_csv(filename)
            print(f"Loaded {len(df)} rows from {filename}")
            return df
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return pd.DataFrame()


def collect_sample_data():
    """
    Collect sample data for testing the model
    """
    collector = NBADataCollector()
    
    # Example: Collect data for 76ers
    print("Collecting 76ers data...")
    team_id = collector.get_team_id_from_abbrev('PHI')
    
    # Get roster
    roster = collector.fetch_team_roster(team_id)
    print(f"Found {len(roster)} players on roster")
    
    # Collect game logs for each player
    all_game_logs = []
    
    for _, player in roster.iterrows():
        player_id = player['PLAYER_ID']
        player_name = player['PLAYER']
        print(f"Fetching game logs for {player_name}...")
        
        game_logs = collector.fetch_player_game_logs(player_id)
        if len(game_logs) > 0:
            all_game_logs.append(game_logs)
        
        time.sleep(0.6)  # Rate limiting
    
    # Combine all game logs
    if all_game_logs:
        combined_df = pd.concat(all_game_logs, ignore_index=True)
        collector.save_data(combined_df, 'data/sixers_game_logs.csv')
        return combined_df
    
    return pd.DataFrame()


if __name__ == "__main__":
    # Test data collection
    collect_sample_data()
