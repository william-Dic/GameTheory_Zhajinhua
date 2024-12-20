import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

# Define the AI strategy that transitions from conservative to moderate
def ai_strategy(hand_strength, player_coins):
    """
    AI Strategy:
    - Conservative when coins <= 3
    - Moderate when coins > 3
    """
    if player_coins <= 3:
        # Conservative logic
        if hand_strength < 7:
            return 'fold'
        elif 7 <= hand_strength <= 9:
            return 'bet1'
        else:
            return 'bet2'
    else:
        # Moderate logic
        if hand_strength < 5:
            return 'fold'
        elif 5 <= hand_strength <= 8:
            return 'bet1'
        else:
            return 'bet2'

# Basic opponent strategies
def conservative_strategy(hand_strength, player_coins):
    if hand_strength < 5:
        return 'fold'
    elif 5 <= hand_strength <= 9:
        return 'bet1'
    else:
        return 'bet2'

def aggressive_strategy(hand_strength, player_coins):
    if hand_strength < 1:
        return 'fold'
    elif 1 <= hand_strength < 5:
        return 'bet1'
    else:
        return 'bet2'

def moderate_strategy(hand_strength, player_coins):
    if hand_strength < 4:
        return 'fold'
    elif 4 <= hand_strength <= 7:
        return 'bet1'
    else:
        return 'bet2'

def random_strategy(hand_strength, player_coins):
    return random.choice(['fold', 'bet1', 'bet2'])

# Composite opponent strategies
def aggressive_moderate_strategy(hand_strength, player_coins):
    """Aggressive when coins >= 5, Moderate otherwise"""
    if player_coins >= 5:
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return moderate_strategy(hand_strength, player_coins)

def aggressive_conservative_strategy(hand_strength, player_coins):
    """Aggressive when coins >= 5, Conservative otherwise"""
    if player_coins >= 5:
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return conservative_strategy(hand_strength, player_coins)

def conservative_aggressive_strategy(hand_strength, player_coins):
    """Conservative when coins <= 5, Aggressive otherwise"""
    if player_coins <= 5:
        return conservative_strategy(hand_strength, player_coins)
    else:
        return aggressive_strategy(hand_strength, player_coins)

def moderate_aggressive_strategy(hand_strength, player_coins):
    """Moderate when coins <= 5, Aggressive otherwise"""
    if player_coins <= 5:
        return moderate_strategy(hand_strength, player_coins)
    else:
        return aggressive_strategy(hand_strength, player_coins)

def adaptive_aggressive_strategy(hand_strength, player_coins):
    """Adapts aggression based on coin count"""
    if player_coins >= 7:
        # Very aggressive
        if hand_strength < 1:
            return 'fold'
        else:
            return 'bet2'
    elif player_coins >= 4:
        # Moderately aggressive
        if hand_strength < 2:
            return 'fold'
        elif hand_strength < 6:
            return 'bet1'
        else:
            return 'bet2'
    else:
        # Conservative
        return conservative_strategy(hand_strength, player_coins)

def cyclic_strategy(hand_strength, player_coins):
    """Cycles between aggressive, moderate, and conservative based on coins"""
    coin_cycle = player_coins % 3
    if coin_cycle == 0:
        return aggressive_strategy(hand_strength, player_coins)
    elif coin_cycle == 1:
        return moderate_strategy(hand_strength, player_coins)
    else:
        return conservative_strategy(hand_strength, player_coins)

def balanced_strategy(hand_strength, player_coins):
    """Balances between strategies based on hand strength and coins"""
    if player_coins <= 3:
        if hand_strength < 3:
            return 'fold'
        elif hand_strength < 7:
            return 'bet1'
        else:
            return 'bet2'
    else:
        if hand_strength < 4:
            return 'fold'
        elif hand_strength < 8:
            return 'bet1'
        else:
            return 'bet2'

def risky_conservative_strategy(hand_strength, player_coins):
    """Conservative with occasional high-risk plays"""
    if random.random() < 0.2:  # 20% chance of aggressive play
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return conservative_strategy(hand_strength, player_coins)

def progressive_strategy(hand_strength, player_coins):
    """Becomes more aggressive as coins increase"""
    aggression_threshold = min(player_coins / 10, 1)  # Scale with coins
    if random.random() < aggression_threshold:
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return moderate_strategy(hand_strength, player_coins)

def coin_aware_strategy(hand_strength, player_coins):
    """Adapts strategy based on exact coin count"""
    if player_coins <= 2:
        return conservative_strategy(hand_strength, player_coins)
    elif player_coins <= 4:
        return moderate_strategy(hand_strength, player_coins)
    elif player_coins <= 6:
        return aggressive_strategy(hand_strength, player_coins)
    else:
        return balanced_strategy(hand_strength, player_coins)

# Mapping opponent strategy names to functions
opponent_strategies = {
    'Conservative': conservative_strategy,
    'Aggressive': aggressive_strategy,
    'Moderate': moderate_strategy,
    'Random': random_strategy,
    'Aggressive-Moderate': aggressive_moderate_strategy,
    'Aggressive-Conservative': aggressive_conservative_strategy,
    'Conservative-Aggressive': conservative_aggressive_strategy,
    'Moderate-Aggressive': moderate_aggressive_strategy,
    'Adaptive-Aggressive': adaptive_aggressive_strategy,
    'Cyclic': cyclic_strategy,
    'Balanced': balanced_strategy,
    'Risky-Conservative': risky_conservative_strategy,
    'Progressive': progressive_strategy,
    'Coin-Aware': coin_aware_strategy
}

def simulate_round(opponent_strategy, player_coins, opponent_coins):
    """Simulate a single round of the game."""
    # Deal hands
    player_hand = random.randint(0, 10)
    opponent_hand = random.randint(0, 10)
    
    # Decide actions
    player_action = ai_strategy(player_hand, player_coins)
    opponent_action = opponent_strategies[opponent_strategy](opponent_hand, opponent_coins)
    
    # Initialize pot
    pot = 0
    
    # Handle Player's action
    if player_action == 'fold':
        player_bet = 0
    elif player_action == 'bet1':
        player_bet = 1 if player_coins >= 1 else 0
        player_coins -= player_bet
        pot += player_bet
    else:  # bet2
        player_bet = 2 if player_coins >= 2 else (1 if player_coins >= 1 else 0)
        player_coins -= player_bet
        pot += player_bet
    
    # Handle Opponent's action
    if opponent_action == 'fold':
        opponent_bet = 0
    elif opponent_action == 'bet1':
        opponent_bet = 1 if opponent_coins >= 1 else 0
        opponent_coins -= opponent_bet
        pot += opponent_bet
    else:  # bet2
        opponent_bet = 2 if opponent_coins >= 2 else (1 if opponent_coins >= 1 else 0)
        opponent_coins -= opponent_bet
        pot += opponent_bet
    
    # Determine outcome
    if player_action == 'fold':
        opponent_coins += pot
    elif opponent_action == 'fold':
        player_coins += pot
    else:
        # Both bet: Compare hands
        if player_hand > opponent_hand:
            player_coins += pot
        elif opponent_hand > player_hand:
            opponent_coins += pot
        else:
            # Tie: Return bets
            player_coins += player_bet
            opponent_coins += opponent_bet
    
    return player_coins, opponent_coins

def simulate_game(opponent_strategy, starting_coins=5, max_rounds=1000):
    """Simulate a complete game."""
    player_coins = starting_coins
    opponent_coins = starting_coins
    rounds = 0
    
    while player_coins > 0 and opponent_coins > 0 and rounds < max_rounds:
        player_coins, opponent_coins = simulate_round(
            opponent_strategy, player_coins, opponent_coins
        )
        rounds += 1
    
    if player_coins > opponent_coins:
        return 'AI'
    elif opponent_coins > player_coins:
        return 'Opponent'
    else:
        return 'Draw'

def run_simulations(num_simulations=10000):
    """Run simulations against all opponent strategies."""
    results = []
    
    for opponent_strategy in tqdm(opponent_strategies.keys(), desc="Simulating strategies"):
        strategy_results = {'AI': 0, 'Opponent': 0, 'Draw': 0}
        
        for _ in range(num_simulations):
            outcome = simulate_game(opponent_strategy)
            strategy_results[outcome] += 1
        
        win_rate = (strategy_results['AI'] / num_simulations) * 100
        results.append({
            'Opponent Strategy': opponent_strategy,
            'AI Wins': strategy_results['AI'],
            'Opponent Wins': strategy_results['Opponent'],
            'Draws': strategy_results['Draw'],
            'Win Rate (%)': win_rate
        })
    
    return pd.DataFrame(results)

def create_win_rate_heatmap(df_results):
    """Create a heatmap showing win rates against different strategies."""
    plt.figure(figsize=(15, 10))
    
    # Prepare data for heatmap
    win_rates = df_results['Win Rate (%)'].values.reshape(-1, 1)
    strategies = df_results['Opponent Strategy'].values
    
    # Create heatmap data
    heatmap_data = pd.DataFrame(win_rates, 
                               index=strategies,
                               columns=['Win Rate'])
    
    # Create heatmap
    sns.heatmap(heatmap_data, 
                annot=True, 
                fmt='.1f',
                cmap='RdYlGn',
                center=50,
                vmin=0,
                vmax=100,
                cbar_kws={'label': 'Win Rate (%)'})
    
    plt.title('AI Win Rate Against Different Strategies')
    plt.tight_layout()
    plt.show()

def create_detailed_bar_plot(df_results):
    """Create a detailed bar plot with win/loss/draw breakdown."""
    plt.figure(figsize=(15, 8))
    
    # Calculate percentages
    total_games = df_results['AI Wins'] + df_results['Opponent Wins'] + df_results['Draws']
    df_results['AI Win %'] = (df_results['AI Wins'] / total_games) * 100
    df_results['Opponent Win %'] = (df_results['Opponent Wins'] / total_games) * 100
    df_results['Draw %'] = (df_results['Draws'] / total_games) * 100
    
    # Create stacked bar chart
    bottom_vals = np.zeros(len(df_results))
    
    for column, color in zip(['AI Win %', 'Opponent Win %', 'Draw %'], 
                           ['#2ecc71', '#e74c3c', '#3498db']):
        plt.bar(df_results['Opponent Strategy'], 
                df_results[column],
                bottom=bottom_vals,
                label=column,
                color=color)
        bottom_vals += df_results[column]
    
    plt.title('Game Outcome Distribution by Strategy')
    plt.xlabel('Opponent Strategy')
    plt.ylabel('Percentage of Games')
    plt.legend(title='Outcome')
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def create_performance_radar(df_results):
    """Create a radar chart showing AI performance metrics."""
    plt.figure(figsize=(12, 12))
    
    # Prepare data for radar chart
    categories = df_results['Opponent Strategy'].values
    values = df_results['Win Rate (%)'].values
    
    # Number of variables
    num_vars = len(categories)
    
    # Compute angle for each axis
    angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
    angles += angles[:1]
    values = np.concatenate((values, [values[0]]))
    
    # Initialize the spider plot
    ax = plt.subplot(111, projection='polar')
    
    # Draw the plot
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    
    # Add labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # Add title
    plt.title('AI Performance Radar Chart\n(Win Rate % by Strategy)', y=1.05)
    
    plt.tight_layout()
    plt.show()

# Run simulations and create visualizations
if __name__ == "__main__":
    print("Running simulations...")
    df_results = run_simulations()

    # Create visualizations
    create_win_rate_heatmap(df_results)
    create_detailed_bar_plot(df_results)
    create_performance_radar(df_results)

    # Print enhanced statistics
    print("\nDetailed Strategy Analysis:")
    print("-" * 60)
    print(df_results.sort_values('Win Rate (%)', ascending=False).to_string(index=False))

    # Calculate and print additional statistics
    print("\nStrategy Performance Summary:")
    print("-" * 60)
    print(f"Best Performance Against: {df_results.loc[df_results['Win Rate (%)'].idxmax(), 'Opponent Strategy']} "
          f"({df_results['Win Rate (%)'].max():.2f}%)")
    print(f"Worst Performance Against: {df_results.loc[df_results['Win Rate (%)'].idxmin(), 'Opponent Strategy']} "
          f"({df_results['Win Rate (%)'].min():.2f}%)")
    print(f"Average Win Rate: {df_results['Win Rate (%)'].mean():.2f}%")
    print(f"Win Rate Standard Deviation: {df_results['Win Rate (%)'].std():.2f}%")

    # Calculate strategy grouping statistics
    print("\nStrategy Group Analysis:")
    print("-" * 60)
    basic_strategies = ['Conservative', 'Aggressive', 'Moderate', 'Random']
    composite_strategies = [s for s in df_results['Opponent Strategy'] if s not in basic_strategies]

    # Calculate strategy grouping statistics
    print("\nStrategy Group Analysis:")
    print("-" * 60)
    basic_strategies = ['Conservative', 'Aggressive', 'Moderate', 'Random']
    composite_strategies = [s for s in df_results['Opponent Strategy'] if s not in basic_strategies]

    basic_avg = df_results[df_results['Opponent Strategy'].isin(basic_strategies)]['Win Rate (%)'].mean()
    composite_avg = df_results[df_results['Opponent Strategy'].isin(composite_strategies)]['Win Rate (%)'].mean()

    print(f"Average Win Rate vs Basic Strategies: {basic_avg:.2f}%")
    print(f"Average Win Rate vs Composite Strategies: {composite_avg:.2f}%")

    # Create performance comparison plot
    plt.figure(figsize=(15, 8))
    strategy_types = ['Basic Strategies', 'Composite Strategies']
    avg_rates = [basic_avg, composite_avg]
    
    plt.bar(strategy_types, avg_rates, color=['#3498db', '#e74c3c'])
    plt.title('AI Performance Against Strategy Types')
    plt.xlabel('Strategy Type')
    plt.ylabel('Average Win Rate (%)')
    plt.axhline(y=50, color='black', linestyle='--', alpha=0.5, label='50% Threshold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Create win rate distribution plot
    plt.figure(figsize=(15, 6))
    sns.boxplot(data=df_results, x='Win Rate (%)', whis=1.5)
    plt.title('Distribution of AI Win Rates')
    plt.axvline(x=50, color='r', linestyle='--', alpha=0.5, label='50% Threshold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Print strategy-specific statistics
    print("\nStrategy-Specific Statistics:")
    print("-" * 60)
    strategy_stats = df_results.groupby('Opponent Strategy').agg({
        'Win Rate (%)': ['mean', 'std', 'min', 'max']
    }).round(2)
    
    strategy_stats.columns = ['Mean Win Rate', 'Std Dev', 'Min Win Rate', 'Max Win Rate']
    print(strategy_stats.to_string())

    # Calculate strategy effectiveness tiers
    print("\nStrategy Effectiveness Tiers:")
    print("-" * 60)
    df_results['Effectiveness'] = pd.qcut(df_results['Win Rate (%)'], 
                                        q=3, 
                                        labels=['Highly Effective vs AI', 
                                               'Moderately Effective', 
                                               'Less Effective vs AI'])
    
    effectiveness_summary = df_results.groupby('Effectiveness')['Opponent Strategy'].apply(list)
    for tier, strategies in effectiveness_summary.items():
        print(f"\n{tier}:")
        for strategy in strategies:
            print(f"- {strategy}")

    # Save results to CSV
    df_results.to_csv('ai_strategy_analysis_results.csv', index=False)
    print("\nResults have been saved to 'ai_strategy_analysis_results.csv'")