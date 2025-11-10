"""
Bet Tracking System

Track your bets and calculate ROI over time
"""

import pandas as pd
from datetime import datetime


class BetTracker:
    def __init__(self, csv_file='bet_history.csv'):
        self.csv_file = csv_file
        try:
            self.bets = pd.read_csv(csv_file)
            self.bets['Date'] = pd.to_datetime(self.bets['Date'])
        except FileNotFoundError:
            self.bets = pd.DataFrame(columns=[
                'Date', 'Player', 'Stat', 'Line', 'Bet_Type', 
                'Prediction', 'Actual', 'Amount', 'Result', 'Profit',
                'Edge_Percent', 'Confidence_Percent', 'Notes'
            ])
    
    def add_bet(self, player, stat, line, bet_type, prediction, amount, 
                edge_pct, confidence_pct, notes=''):
        """
        Add a new bet to track
        
        Parameters:
        - player: Player name
        - stat: 'PTS', 'REB', 'AST', etc.
        - line: Betting line number
        - bet_type: 'OVER' or 'UNDER'
        - prediction: Model prediction
        - amount: Dollar amount wagered
        - edge_pct: Edge percentage from model
        - confidence_pct: Win probability
        - notes: Any additional notes
        """
        new_bet = {
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Player': player,
            'Stat': stat,
            'Line': line,
            'Bet_Type': bet_type,
            'Prediction': prediction,
            'Actual': None,
            'Amount': amount,
            'Result': 'Pending',
            'Profit': None,
            'Edge_Percent': edge_pct,
            'Confidence_Percent': confidence_pct,
            'Notes': notes
        }
        
        self.bets = pd.concat([self.bets, pd.DataFrame([new_bet])], ignore_index=True)
        self.save()
        
        print(f"✓ Bet added: {player} {bet_type} {line} {stat} (${amount})")
    
    def update_result(self, index, actual_value):
        """
        Update bet result after game is played
        
        Parameters:
        - index: Row index in DataFrame
        - actual_value: Actual stat value achieved
        """
        bet = self.bets.loc[index]
        
        # Determine if bet won
        if bet['Bet_Type'] == 'OVER':
            won = actual_value > bet['Line']
        else:  # UNDER
            won = actual_value < bet['Line']
        
        # Calculate profit (assuming -110 odds)
        if won:
            profit = bet['Amount'] * 0.909  # Win amount at -110
            result = 'Win'
        else:
            profit = -bet['Amount']
            result = 'Loss'
        
        # Update DataFrame
        self.bets.at[index, 'Actual'] = actual_value
        self.bets.at[index, 'Result'] = result
        self.bets.at[index, 'Profit'] = profit
        
        self.save()
        
        print(f"✓ Bet updated: {bet['Player']} scored {actual_value} "
              f"({result}, ${profit:+.2f})")
        
        return profit
    
    def get_pending_bets(self):
        """Get all pending bets"""
        return self.bets[self.bets['Result'] == 'Pending']
    
    def get_summary(self):
        """Get summary statistics"""
        completed = self.bets[self.bets['Result'] != 'Pending']
        
        if len(completed) == 0:
            return "No completed bets yet."
        
        total_bets = len(completed)
        wins = len(completed[completed['Result'] == 'Win'])
        losses = len(completed[completed['Result'] == 'Loss'])
        win_rate = wins / total_bets * 100
        
        total_wagered = completed['Amount'].sum()
        total_profit = completed['Profit'].sum()
        roi = (total_profit / total_wagered) * 100
        
        summary = f"""
{'='*80}
BET TRACKING SUMMARY
{'='*80}

Total Bets: {total_bets}
Wins: {wins}
Losses: {losses}
Win Rate: {win_rate:.1f}%

Total Wagered: ${total_wagered:.2f}
Total Profit: ${total_profit:+.2f}
ROI: {roi:+.2f}%

{'='*80}
RECENT BETS:
{'='*80}
"""
        recent = completed.tail(10)[['Date', 'Player', 'Bet_Type', 'Line', 
                                     'Actual', 'Result', 'Profit']]
        summary += recent.to_string(index=False)
        
        return summary
    
    def save(self):
        """Save to CSV"""
        self.bets.to_csv(self.csv_file, index=False)
    
    def export_detailed_report(self, filename='bet_report.csv'):
        """Export detailed report"""
        self.bets.to_csv(filename, index=False)
        print(f"Report exported to {filename}")


# Example usage
if __name__ == "__main__":
    tracker = BetTracker()
    
    # Add example bets
    print("\nAdding example bets...")
    
    tracker.add_bet(
        player='Tyrese Maxey',
        stat='PTS',
        line=25.5,
        bet_type='OVER',
        prediction=29.8,
        amount=25,
        edge_pct=8.2,
        confidence_pct=68.0,
        notes='Embiid out due to load management'
    )
    
    tracker.add_bet(
        player='Tobias Harris',
        stat='PTS',
        line=17.5,
        bet_type='OVER',
        prediction=19.2,
        amount=15,
        edge_pct=5.3,
        confidence_pct=61.0,
        notes='Embiid out due to load management'
    )
    
    # Show pending bets
    print("\n" + "="*80)
    print("PENDING BETS:")
    print("="*80)
    pending = tracker.get_pending_bets()
    if len(pending) > 0:
        print(pending[['Player', 'Bet_Type', 'Line', 'Stat', 'Amount', 'Prediction']].to_string(index=False))
    
    # Simulate updating results
    print("\n" + "="*80)
    print("UPDATING RESULTS (Example):")
    print("="*80)
    
    if len(pending) >= 2:
        tracker.update_result(pending.index[0], 31)  # Maxey scored 31
        tracker.update_result(pending.index[1], 16)  # Harris scored 16
    
    # Show summary
    print("\n" + tracker.get_summary())
    
    print("\n" + "="*80)
    print("HOW TO USE:")
    print("="*80)
    print("""
1. After placing a bet, add it to the tracker:
   
   tracker.add_bet(
       player='Player Name',
       stat='PTS',
       line=25.5,
       bet_type='OVER',
       prediction=28.5,
       amount=20,
       edge_pct=6.5,
       confidence_pct=65.0
   )

2. After the game, update the result:
   
   pending = tracker.get_pending_bets()
   # Find the index of your bet
   tracker.update_result(index=0, actual_value=27)

3. Check your performance:
   
   print(tracker.get_summary())

4. Export detailed report:
   
   tracker.export_detailed_report('my_bets_2024.csv')
    """)
