import math
import random
import os
from copy import deepcopy
from typing import List, Tuple, Optional, Dict

class ZhaJinHuaState:
    """Represents a state in the Zha Jin Hua game"""
    def __init__(self, player_hand: List[str], player_coins: int, opponent_coins: int,
                 player_bet: int, opponent_bet: int, is_dealer: bool):
        self.player_hand = player_hand
        self.player_coins = player_coins
        self.opponent_coins = opponent_coins
        self.player_bet = player_bet
        self.opponent_bet = opponent_bet
        self.is_dealer = is_dealer
        self.game_over = False
        self.winner = None

    def get_possible_actions(self) -> List[str]:
        """Returns list of possible actions in current state"""
        actions = ['fold']
        min_bet = max(self.opponent_bet - self.player_bet, 1)
        
        # Can only bet if we have enough coins
        if self.player_coins >= min_bet:
            actions.append('bet1')
        if self.player_coins >= max(2, min_bet):
            actions.append('bet2')
            
        return actions

    def is_terminal(self) -> bool:
        """Checks if the state is terminal"""
        return (self.game_over or 
                self.player_coins <= 0 or 
                self.opponent_coins <= 0 or
                (self.player_bet > 0 and self.opponent_bet > 0))

class MCTSNode:
    """Node in the MCTS tree"""
    def __init__(self, state: ZhaJinHuaState, parent: Optional['MCTSNode'] = None, action: Optional[str] = None):
        self.state = state
        self.parent = parent
        self.action = action  # Action that led to this state
        self.children: Dict[str, MCTSNode] = {}
        self.visits = 0
        self.value = 0.0
        self.untried_actions = state.get_possible_actions()

    def is_fully_expanded(self) -> bool:
        """Checks if all possible actions have been tried"""
        return len(self.untried_actions) == 0

    def best_child(self, c_param: float = 1.414) -> 'MCTSNode':
        """Select best child node using UCB1 formula"""
        choices = [(child,
                   child.value / child.visits + c_param * math.sqrt(2 * math.log(self.visits) / child.visits))
                  for action, child in self.children.items()]
        return max(choices, key=lambda x: x[1])[0]

    def rollout_policy(self, possible_actions: List[str]) -> str:
        """Random policy for rollout phase"""
        return random.choice(possible_actions)

class ZhaJinHuaScoreCalculator:
    """Calculates scores for Zha Jin Hua hands"""
    @staticmethod
    def calculate_score(hand: List[str]) -> Tuple[int, int]:
        """
        Calculate score for Zha Jin Hua hand
        Returns (hand_type_rank, high_card_value)
        """
        # Parse cards from filenames
        cards = []
        for card_path in hand:
            filename = os.path.basename(card_path)
            print(f"Processing filename: {filename}")  # Debug print
            
            # Split filename and extract rank and suit
            # Expected format is like "2_of_hearts.png" or similar
            try:
                # Remove .png extension first
                name_without_ext = filename.split('.')[0]
                parts = name_without_ext.split('_')
                
                # Extract rank from the first part
                rank = parts[0]
                
                # Extract suit from the last part
                suit = parts[-1]
                
                print(f"Extracted rank: {rank}, suit: {suit}")  # Debug print
                
                # Convert rank to numeric value
                rank_value = {
                    'ace': 14, 'king': 13, 'queen': 12, 'jack': 11,
                    '10': 10, '9': 9, '8': 8, '7': 7,
                    '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
                }.get(rank.lower(), int(rank) if rank.isdigit() else 0)
                
                cards.append((rank_value, suit))
                
            except Exception as e:
                print(f"Error processing card {filename}: {str(e)}")
                continue
        
        if not cards:  # If no cards were successfully processed
            return 2, 2  # Return lowest possible score
        
        # Sort cards by value for easier comparison
        cards.sort(reverse=True)
        values = [card[0] for card in cards]
        suits = [card[1] for card in cards]
        
        # Check for Three of a Kind (豹子)
        if len(set(values)) == 1:
            return 7, max(values)
        
        # Check for Flush (同花)
        is_flush = len(set(suits)) == 1
        
        # Check for Straight (顺子)
        is_straight = False
        straight_value = 0
        
        # Special case: Ace-2-3 straight
        if set(values) == {14, 2, 3}:
            is_straight = True
            straight_value = 3
        # Normal straight
        elif max(values) - min(values) == 2 and len(set(values)) == 3:
            is_straight = True
            straight_value = max(values)
        
        # Straight Flush (同花顺)
        if is_straight and is_flush:
            return 6, straight_value or max(values)
        
        # Flush (同花)
        if is_flush:
            return 5, max(values)
        
        # Straight (顺子)
        if is_straight:
            return 4, straight_value or max(values)
        
        # Pair (对子)
        if len(set(values)) == 2:
            for value in values:
                if values.count(value) == 2:
                    return 3, value
        
        # High Card (单张)
        return 2, max(values)

class MCTS:
    """Monte Carlo Tree Search implementation for Zha Jin Hua"""
    def __init__(self, score_calculator: ZhaJinHuaScoreCalculator):
        self.score_calculator = score_calculator

    def get_best_action(self, root_state: ZhaJinHuaState, iterations: int = 1000) -> str:
        root = MCTSNode(root_state)
        
        for _ in range(iterations):
            node = root
            state = deepcopy(root_state)
            
            # Selection
            while not node.state.is_terminal() and node.is_fully_expanded():
                node = node.best_child()
                state = self.simulate_action(state, node.action)
            
            # Expansion
            if not node.state.is_terminal() and not node.is_fully_expanded():
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)
                state = self.simulate_action(state, action)
                node.children[action] = MCTSNode(state, node, action)
                node = node.children[action]
            
            # Simulation
            while not state.is_terminal():
                possible_actions = state.get_possible_actions()
                action = node.rollout_policy(possible_actions)
                state = self.simulate_action(state, action)
            
            # Backpropagation
            reward = self.calculate_reward(state)
            while node is not None:
                node.visits += 1
                node.value += reward
                node = node.parent

        # Return best action based on highest visit count
        return max(root.children.items(), key=lambda x: x[1].visits)[0]

    def simulate_action(self, state: ZhaJinHuaState, action: str) -> ZhaJinHuaState:
        """Simulates an action and returns new state"""
        new_state = deepcopy(state)
        
        if action == 'fold':
            new_state.game_over = True
            total_pot = new_state.player_bet + new_state.opponent_bet
            if new_state.is_dealer:
                new_state.opponent_coins += total_pot
            else:
                new_state.player_coins += total_pot
            return new_state
            
        elif action.startswith('bet'):
            bet_amount = int(action[3])
            min_bet = max(new_state.opponent_bet - new_state.player_bet, 1)
            bet_amount = max(bet_amount, min_bet)
            
            if new_state.player_coins >= bet_amount:
                new_state.player_bet += bet_amount
                new_state.player_coins -= bet_amount
                
                # Simulate opponent response
                if not new_state.is_terminal():
                    self.simulate_opponent_action(new_state)
                    
        return new_state

    def simulate_opponent_action(self, state: ZhaJinHuaState) -> None:
        """Simulates opponent's action"""
        action = random.choice(['fold', 'bet1', 'bet2'])
        
        if action == 'fold':
            state.game_over = True
            total_pot = state.player_bet + state.opponent_bet
            state.player_coins += total_pot
        else:
            bet_amount = 1 if action == 'bet1' else 2
            min_bet = max(state.player_bet - state.opponent_bet, 1)
            bet_amount = max(bet_amount, min_bet)
            
            if state.opponent_coins >= bet_amount:
                state.opponent_bet += bet_amount
                state.opponent_coins -= bet_amount

    def calculate_reward(self, state: ZhaJinHuaState) -> float:
        """Calculate reward for terminal state"""
        if state.game_over:
            return 1.0 if state.player_coins > state.opponent_coins else -1.0
            
        # If we reach showdown, compare hands
        player_score = self.score_calculator.calculate_score(state.player_hand)
        # For opponent's unknown cards, we use average score from possible hands
        avg_opponent_score = self.estimate_opponent_average_score()
        
        # Compare hand types first (first element of the tuple)
        if player_score[0] > 3.5:  # If player has better than a pair
            return 1.0
        elif player_score[0] < 3.5:  # If player has worse than a pair
            return -1.0
        else:  # If hands are equal type, compare high cards
            # Normalize the high card value to a probability
            return (player_score[1] - 7) / 7  # Will give value between -1 and 1

    def estimate_opponent_average_score(self) -> float:
        """Estimates average score of opponent's possible hands"""
        # Returns 3.5 as baseline (between pair and straight)
        return 3.5
    
class ZhaJinHuaAI:
    """AI advisor for Zha Jin Hua game"""
    def __init__(self, score_calculator: ZhaJinHuaScoreCalculator):
        self.score_calculator = score_calculator
        self.mcts = MCTS(score_calculator)

    def get_suggestion(self, state: ZhaJinHuaState) -> str:
        """Gets AI suggestion for the current game state"""
        # Get best action using MCTS
        best_action = self.mcts.get_best_action(state, iterations=500)

        # Generate suggestion message
        player_score = self.score_calculator.calculate_score(state.player_hand)
        suggestion_msg = f"Current hand: {self.get_hand_type_name(player_score[0])}\n"
        suggestion_msg += f"Hand strength: {self.get_hand_strength(player_score)}\n"
        suggestion_msg += f"Suggested action: {self.format_action(best_action)}\n"
        suggestion_msg += self.get_action_explanation(best_action, player_score)

        return suggestion_msg

    @staticmethod
    def get_hand_type_name(type_value: int) -> str:
        """Convert numeric hand type to string description"""
        hand_types = {
            7: "Three of a Kind (豹子)",
            6: "Straight Flush (同花顺)",
            5: "Flush (同花)",
            4: "Straight (顺子)",
            3: "Pair (对子)",
            2: "High Card (单张)"
        }
        return hand_types.get(type_value, "Unknown")

    @staticmethod
    def get_hand_strength(score: Tuple[int, int]) -> str:
        """Convert hand score to descriptive strength"""
        type_value, high_card = score
        if type_value >= 6:
            return "Very Strong"
        elif type_value >= 4:
            return "Strong"
        elif type_value == 3:
            return "Moderate"
        else:
            return "Weak" if high_card < 10 else "Moderate"

    @staticmethod
    def format_action(action: str) -> str:
        """Format action into readable text"""
        if action == 'fold':
            return "Fold"
        elif action == 'bet1':
            return "Bet 1 coin"
        elif action == 'bet2':
            return "Bet 2 coins"
        return "Unknown action"

    @staticmethod
    def get_action_explanation(action: str, score: Tuple[int, int]) -> str:
        """Generate explanation for suggested action"""
        type_value, high_card = score
        
        if action == 'fold':
            if type_value <= 2:
                return "Your hand is weak. Better to fold and save coins for better opportunities."
            return "Despite having a decent hand, the betting situation suggests folding is optimal."
            
        elif action.startswith('bet'):
            if type_value >= 6:
                return "You have a very strong hand. Betting is likely to be profitable."
            elif type_value >= 4:
                return "Your hand is strong. A bet could pressure your opponent."
            elif type_value == 3:
                return "You have a pair. Consider betting to build the pot."
            else:
                return "High card only, but betting might work as a bluff."
                
        return "Consider the pot odds and your opponent's likely holdings."