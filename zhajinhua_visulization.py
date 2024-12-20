import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import product
from tqdm import tqdm  # For progress bars

# Define strategies
def conservative_strategy(hand_strength, player_coins):
    """
    Conservative Strategy:
    - Fold if hand strength is below 5.
    - Bet 1 coin if hand_strength between 5 and 9.
    - Bet 2 coins if hand_strength is 10.
    """
    if hand_strength < 5:
        return 'fold'
    elif 5 <= hand_strength <= 9:
        return 'bet1'
    else:
        return 'bet2'

def aggressive_strategy(hand_strength, player_coins):
    """
    Aggressive Strategy:
    - Fold if hand strength is 0.
    - Bet 1 coin if hand_strength between 1 and 4.
    - Bet 2 coins if hand_strength is 5 or above.
    """
    if hand_strength < 1:
        return 'fold'
    elif 1 <= hand_strength < 5:
        return 'bet1'
    else:
        return 'bet2'

def moderate_strategy(hand_strength, player_coins):
    """
    Moderate Strategy:
    - Fold if hand strength is below 4.
    - Bet 1 coin if hand_strength between 4 and 7.
    - Bet 2 coins if hand_strength is 8 or above.
    """
    if hand_strength < 4:
        return 'fold'
    elif 4 <= hand_strength <= 7:
        return 'bet1'
    else:
        return 'bet2'

def random_strategy(hand_strength, player_coins):
    """
    Random Strategy:
    - Randomly choose to fold, bet 1, or bet 2 coins.
    """
    return random.choice(['fold', 'bet1', 'bet2'])

# Composite Strategies
def aggressive_moderate_strategy(hand_strength, player_coins):
    """
    Aggressive-Moderate Strategy:
    - Aggressive when player_coins >= 6.
    - Moderate otherwise.
    """
    if player_coins >= 5:
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return moderate_strategy(hand_strength, player_coins)

def aggressive_conservative_strategy(hand_strength, player_coins):
    """
    Aggressive-Conservative Strategy:
    - Aggressive when player_coins >= 6.
    - Conservative otherwise.
    """
    if player_coins >= 5:
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return conservative_strategy(hand_strength, player_coins)

def conservative_aggressive_strategy(hand_strength, player_coins):
    """
    Conservative-Aggressive Strategy:
    - Conservative when player_coins <= 6.
    - Aggressive otherwise.
    """
    if player_coins <= 5:
        return conservative_strategy(hand_strength, player_coins)
    else:
        return aggressive_strategy(hand_strength, player_coins)

def moderate_aggressive_strategy(hand_strength, player_coins):
    """
    Moderate-Aggressive Strategy:
    - Moderate when player_coins <= 6.
    - Aggressive otherwise.
    """
    if player_coins <= 5:
        return moderate_strategy(hand_strength, player_coins)
    else:
        return aggressive_strategy(hand_strength, player_coins)

# Mapping strategy names to functions
strategy_functions = {
    'Conservative': conservative_strategy,
    'Aggressive': aggressive_strategy,
    'Moderate': moderate_strategy,
    'Random': random_strategy,
    'Aggressive-Moderate': aggressive_moderate_strategy,
    'Aggressive-Conservative': aggressive_conservative_strategy,
    'Conservative-Aggressive': conservative_aggressive_strategy,
    'Moderate-Aggressive': moderate_aggressive_strategy
}

def simulate_round(player_strategy, opponent_strategy, player_coins, opponent_coins):
    """
    Simulate a single round of the game.
    
    Returns updated player_coins and opponent_coins.
    """
    # Deal hands
    player_hand = random.randint(0, 10)
    opponent_hand = random.randint(0, 10)
    
    # Decide actions based on strategies and hands
    player_action = strategy_functions[player_strategy](player_hand, player_coins)
    opponent_action = strategy_functions[opponent_strategy](opponent_hand, opponent_coins)
    
    # Initialize pot
    pot = 0
    
    # Handle Player's action
    if player_action == 'fold':
        player_bet = 0
    elif player_action == 'bet1':
        player_bet = 1 if player_coins >= 1 else 0
        player_coins -= player_bet
        pot += player_bet
    elif player_action == 'bet2':
        player_bet = 2 if player_coins >= 2 else (1 if player_coins >=1 else 0)
        player_coins -= player_bet
        pot += player_bet
    else:
        player_bet = 0  # Default to fold if undefined action
    
    # Handle Opponent's action
    if opponent_action == 'fold':
        opponent_bet = 0
    elif opponent_action == 'bet1':
        opponent_bet = 1 
        opponent_coins -= opponent_bet
        pot += opponent_bet
    elif opponent_action == 'bet2':
        opponent_bet = 2 
        opponent_coins -= opponent_bet
        pot += opponent_bet
    else:
        opponent_bet = 0  # Default to fold if undefined action
    
    # Determine outcome
    if player_action.startswith('fold') or opponent_action.startswith('fold'):
        # Both folded: No change
        pass
    
    else:
        # Both bet: Compare hands
        if player_hand > opponent_hand:
            player_coins += pot
        elif opponent_hand > player_hand:
            opponent_coins += pot
        else:
            # Tie: Return bets to players
            player_coins += player_bet
            opponent_coins += opponent_bet
    
    return player_coins, opponent_coins

def simulate_game(player_strategy, opponent_strategy, starting_coins=5, max_rounds=1000):
    """
    Simulate a single game until one player runs out of coins.
    
    Returns 'Player' if the player wins, 'Opponent' if the opponent wins, or 'Draw' if max_rounds reached.
    """
    player_coins = starting_coins
    opponent_coins = starting_coins
    rounds = 0
    
    while player_coins > 0 and opponent_coins > 0 and rounds < max_rounds:
        player_coins, opponent_coins = simulate_round(
            player_strategy, opponent_strategy, player_coins, opponent_coins
        )
        rounds += 1
    
    if player_coins > 0 and opponent_coins == 0:
        return 'Player'
    elif opponent_coins > 0 and player_coins == 0:
        return 'Opponent'
    else:
        return 'Draw'

def simulate_multiple_games(player_strategy, opponent_strategy, num_simulations=10000):
    """
    Simulate multiple games and calculate the player's win rate.
    
    Returns the number of Player wins, Opponent wins, Draws, and Player win rate (%).
    """
    results = {'Player': 0, 'Opponent': 0, 'Draw': 0}
    for _ in range(num_simulations):
        outcome = simulate_game(player_strategy, opponent_strategy)
        results[outcome] += 1
    
    # Calculate win rate: Player wins / Total simulations * 100
    win_rate = (results['Player']) / num_simulations * 100
    return results['Player'], results['Opponent'], results['Draw'], win_rate

# Generate all strategy combinations
strategies = list(strategy_functions.keys())
strategy_combinations = list(product(strategies, strategies))  # 8x8=64 combinations

# Simulate games for each combination
simulation_results = []
num_simulations_per_pair = 10000  # Increased simulations for reliability

print("Starting simulations...")
for player_strat, opponent_strat in tqdm(strategy_combinations, desc="Strategy Pairs"):
    player_wins, opponent_wins, draws, win_rate = simulate_multiple_games(
        player_strat, opponent_strat, num_simulations=num_simulations_per_pair
    )
    simulation_results.append({
        'Player Strategy': player_strat,
        'Opponent Strategy': opponent_strat,
        'Player Wins': player_wins,
        'Opponent Wins': opponent_wins,
        'Draws': draws,
        'Win Rate (%)': win_rate
    })

# Create a DataFrame
df_results = pd.DataFrame(simulation_results)
print("\nSimulation Results:")
print(df_results)

# Pivot the DataFrame for heatmap
heatmap_data = df_results.pivot(
    index='Player Strategy',
    columns='Opponent Strategy',
    values='Win Rate (%)'
)

# Set up the matplotlib figure for Heatmap
plt.figure(figsize=(16, 12))

# Create the heatmap
sns.heatmap(
    heatmap_data, 
    annot=True, 
    fmt=".1f", 
    cmap='YlGnBu', 
    linewidths=.5, 
    linecolor='gray'
)

# Add title and labels
plt.title('Player Win Rate (%) by Strategy Combination (10,000 Simulations Each)', fontsize=16)
plt.xlabel('Opponent Strategy', fontsize=14)
plt.ylabel('Player Strategy', fontsize=14)

# Adjust layout for better appearance
plt.tight_layout()

# Show the heatmap
plt.show()

# Alternative Visualization: Grouped Bar Chart
plt.figure(figsize=(20, 12))
sns.barplot(
    x='Opponent Strategy',
    y='Win Rate (%)',
    hue='Player Strategy',
    data=df_results,
    palette='viridis'
)

# Add title and labels
plt.title('Player Win Rate (%) by Strategy Combination (10,000 Simulations Each)', fontsize=16)
plt.xlabel('Opponent Strategy', fontsize=14)
plt.ylabel('Win Rate (%)', fontsize=14)

# Move the legend outside the plot
plt.legend(title='Player Strategy', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)

# Adjust layout for better appearance
plt.tight_layout()

# Show the bar chart
plt.show()
