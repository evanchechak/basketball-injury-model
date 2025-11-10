# NBA Injury Impact Betting Model

A data analytics model that identifies profitable betting opportunities based on player injuries and absences in NBA games. The model analyzes historical performance data to predict how teammates perform when star players are out, then compares these predictions to betting lines to find edges.

## 🎯 What This Does

When a star player like Joel Embiid is out due to injury or load management:
1. **Analyzes historical impact** - How did teammates perform in past games when the star was absent?
2. **Predicts future performance** - What should we expect tonight?
3. **Finds betting edges** - Where are the betting lines mispriced based on our analysis?

## 📊 Example Output

```
ANALYZING IMPACT: Joel Embiid OUT
================================================================================

Top Affected Teammates:
--------------------------------------------------------------------------------
  ✓ Tyrese Maxey:
      Avg with Joel Embiid: 24.3
      Avg without Joel Embiid: 30.1
      Difference: +5.8
      Betting Line: 25.5
      Prediction: 30.1
      → OVER (Edge: 8.2%)

BETTING OPPORTUNITIES FOUND: 1
================================================================================
```

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run Examples (with sample data)

```bash
python examples.py
```

This will run 4 example scenarios with simulated data:
- Basic impact analysis
- Finding betting opportunities
- Comparing multiple scenarios
- Optimal bet sizing with Kelly Criterion

### 3. Use with Real Data

```python
from injury_impact_model import InjuryImpactModel
from data_collector import NBADataCollector
import pandas as pd

# Option A: Collect data from NBA Stats API
collector = NBADataCollector()
team_id = collector.get_team_id_from_abbrev('PHI')  # 76ers
roster = collector.fetch_team_roster(team_id)

# Collect game logs for all players
game_logs = []
for _, player in roster.iterrows():
    logs = collector.fetch_player_game_logs(player['PLAYER_ID'])
    game_logs.append(logs)

player_stats = pd.concat(game_logs, ignore_index=True)

# Option B: Load your own CSV files
player_stats = pd.read_csv('your_player_stats.csv')
games = pd.read_csv('your_games.csv')

# Initialize model
model = InjuryImpactModel()
model.load_data(games, player_stats)

# Find opportunities when a star is out
betting_lines = {
    'Tyrese Maxey': 25.5,
    'Tobias Harris': 17.5
}

opportunities = model.find_betting_opportunities(
    injured_player_id=203954,  # Joel Embiid's ID
    injured_player_name='Joel Embiid',
    team_id=1610612755,  # 76ers
    betting_lines=betting_lines,
    stat='PTS',
    min_edge=0.05  # Require 5% edge
)

print(opportunities)
```

## 📁 File Structure

```
nba_betting_model/
├── injury_impact_model.py   # Core model logic
├── data_collector.py         # NBA Stats API data collection
├── examples.py               # Example usage with sample data
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── data/                     # Your data files go here
    ├── player_stats.csv
    └── games.csv
```

## 🔧 Key Features

### 1. Injury Impact Analysis
```python
# Analyze how teammates perform when star is out
impacts = model.analyze_injury_impact(
    injured_player_id=star_id,
    team_id=team_id,
    stat='PTS'
)
```

### 2. Statistical Significance Testing
- T-tests to verify that differences aren't just random
- Sample size validation
- Confidence intervals for predictions

### 3. Betting Edge Calculation
- Expected value (EV) calculations
- Probability estimates using normal distribution
- Configurable minimum edge thresholds

### 4. Multiple Stats Support
```python
# Works with any stat
stat='PTS'   # Points
stat='REB'   # Rebounds
stat='AST'   # Assists
stat='PRA'   # Points + Rebounds + Assists
```

## 📊 Required Data Format

### Player Stats CSV
Your data should include these columns:
- `PLAYER_ID` - Unique player identifier
- `PLAYER_NAME` - Player name
- `TEAM_ID` - Team identifier
- `GAME_ID` - Unique game identifier
- `GAME_DATE` - Date of game
- `MATCHUP` - Team matchup (e.g., "PHI vs. BOS")
- `MIN` - Minutes played
- `PTS` - Points scored
- `REB` - Rebounds
- `AST` - Assists
- Other stats as needed

### Games CSV
- `GAME_ID` - Unique game identifier
- `GAME_DATE` - Date
- `MATCHUP` - Team matchup
- `TEAM_ID` - Team identifier

## 🎲 Using with Real Betting Lines

### Getting Current Lines

Check these sportsbooks for player prop lines:
- DraftKings
- FanDuel
- BetMGM
- Caesars
- PointsBet

### Example Daily Workflow

```python
# 1. Check NBA injury report (6-7 PM ET)
# Visit: https://www.nba.com/news/injury-report

# 2. When you see a star player is OUT:
injured_player = "Joel Embiid"
team = "PHI"

# 3. Get betting lines from sportsbook
betting_lines = {
    'Tyrese Maxey': 26.5,
    'Tobias Harris': 18.5,
    "De'Anthony Melton": 13.5
}

# 4. Run the model
opportunities = model.find_betting_opportunities(...)

# 5. Place bets on opportunities with 5%+ edge
# 6. Track results!
```

## 📈 Expected Performance

With proper usage:
- **Win Rate Target**: 53-55% (accounting for -110 odds)
- **ROI Target**: 3-8% per bet
- **Sample Size**: Need 50+ bets to see true edge
- **Variance**: Expect losing streaks even with an edge

## ⚠️ Important Notes

### Bankroll Management
```python
# Use Kelly Criterion for bet sizing
prob_win = 0.58  # 58% win probability
odds = 0.909     # -110 odds
kelly = (odds * prob_win - (1 - prob_win)) / odds
conservative_kelly = kelly * 0.25  # Use 25% of full Kelly

# With $1,000 bankroll
bet_amount = 1000 * conservative_kelly
```

### Risk Factors
1. **Line movement** - Lines may move after injury announcement
2. **Sample size** - Need at least 5-10 games without star player
3. **Context changes** - Team strategies evolve over seasons
4. **Other injuries** - Multiple injuries complicate predictions
5. **Variance** - Short-term results will vary significantly

### Best Practices
- ✅ Only bet when edge is 5%+
- ✅ Track all bets in a spreadsheet
- ✅ Review results after 50+ bets
- ✅ Update data regularly (weekly)
- ✅ Consider multiple sportsbooks for best lines
- ❌ Don't bet on every opportunity
- ❌ Don't chase losses
- ❌ Don't bet more than 5% of bankroll on single bet

## 🔬 Advanced Features to Add

Want to improve the model? Consider adding:

1. **Opponent strength** - Defensive ratings
2. **Home/away splits** - Performance differences
3. **Back-to-back games** - Fatigue factor
4. **Rest days** - Impact on performance
5. **Recent form** - Weighted recent games more
6. **Pace adjustments** - Fast vs slow teams
7. **Lineup combinations** - Which players play together
8. **Line shopping** - Compare multiple sportsbooks

## 📚 Learning Resources

### Sports Betting Math
- [Expected Value in Sports Betting](https://en.wikipedia.org/wiki/Expected_value)
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)

### NBA Analytics
- [NBA Stats API](https://stats.nba.com/)
- [Basketball Reference](https://www.basketball-reference.com/)

### Responsible Gambling
- Only bet what you can afford to lose
- Set strict bankroll limits
- Take breaks if losing
- Seek help if needed: [NCPG](https://www.ncpgambling.org/)

## 🤝 Contributing

Want to improve this model? Ideas:
- Add more sophisticated prediction models (neural networks, XGBoost)
- Integrate real-time odds APIs
- Build a web interface
- Add automated alerts for opportunities
- Backtesting framework

## ⚖️ Legal Disclaimer

This tool is for educational and informational purposes only. Sports betting may be illegal in your jurisdiction. Always comply with local laws. Past performance does not guarantee future results. Bet responsibly.

## 📝 License

MIT License - Feel free to use and modify!

---

## 🎓 How It Works (Technical Details)

### Step 1: Data Collection
- Fetches game-by-game stats for all players
- Tracks which games star players missed
- Builds historical database

### Step 2: Impact Measurement
```python
# For each teammate, compare:
performance_with_star = avg(games where star played)
performance_without_star = avg(games where star was out)
impact = performance_without_star - performance_with_star
```

### Step 3: Statistical Validation
- T-test to confirm significance
- Minimum sample size requirements
- Calculate standard deviation for predictions

### Step 4: Prediction
- Use historical "without star" average
- Adjust for opponent, home/away, etc.
- Generate confidence intervals

### Step 5: Edge Detection
```python
# Calculate probability of going OVER the line
z_score = (betting_line - prediction) / std_dev
prob_over = 1 - normal_cdf(z_score)

# Calculate expected value
ev_over = (prob_over * 0.909) - (1 - prob_over)
ev_under = ((1 - prob_over) * 0.909) - prob_over

# Bet if edge > threshold
if ev_over > 0.05:
    recommend = "OVER"
```

## 🎯 Example: Real Scenario

**Situation**: Joel Embiid ruled OUT vs. Celtics

**Historical Data**:
- Tyrese Maxey averages 24.1 PPG with Embiid (52 games)
- Tyrese Maxey averages 29.8 PPG without Embiid (16 games)
- Difference: +5.7 PPG (p=0.003, highly significant)

**Current Betting Line**: Maxey O/U 25.5 points

**Model Output**:
- Prediction: 29.8 points
- Probability of OVER: 68%
- Expected Value: +9.4%
- **Recommendation: BET OVER 25.5 (-110)**

**Optimal Bet Size** (with $1,000 bankroll):
- Kelly Criterion: 3.2% = $32
- Conservative (25% Kelly): $8

**Result Tracking**:
- If Maxey scores 26+: Win $7.27
- If Maxey scores <26: Lose $8
- Expected profit per bet: $0.75 (9.4% ROI)

---

Good luck and bet responsibly! 🍀
