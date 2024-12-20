import os
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from MCTS_agent import ZhaJinHuaScoreCalculator, ZhaJinHuaState, ZhaJinHuaAI

class PlayerAction:
    def __init__(self, gui, strategy="human"):
        self.gui = gui
        self.strategy = strategy

    def act(self):
        if self.strategy == "random":
            # Random strategy: randomly choose bet1, bet2, or fold
            action = random.choice(["bet1", "bet2", "fold"])
            if action == "fold":
                self.fold()
            else:
                self.bet(int(action[3]))

    def fold(self):
        self.gui.log_action("You folded.")
        self.gui.result_label.config(text="You folded. Opponent takes the pot.", fg="red")
        total_pot = self.gui.player_bet + self.gui.opponent_bet
        self.gui.opponent_coins += total_pot
        self.gui.player_bet = 0
        self.gui.opponent_bet = 0
        self.gui.update_coins()
        self.gui.check_game_over()
        
        self.gui.simulator.Dealer = 1 - self.gui.simulator.Dealer
        self.gui.log_action(f"Dealer switched to {'Opponent' if self.gui.simulator.Dealer == 1 else 'You'}.")

        self.gui.reset_game_with_delay()
        self.gui.disable_player_actions()

    def bet(self, amount=None):
        if self.strategy == "human":
            if amount is None:
                self.gui.result_label.config(text="Invalid bet amount.", fg="red")
                return
            bet_amount = amount
            # Get AI suggestion for human player
            current_state = ZhaJinHuaState(
                player_hand=self.gui.player_hand,
                player_coins=self.gui.player_coins,
                opponent_coins=self.gui.opponent_coins,
                player_bet=self.gui.player_bet,
                opponent_bet=self.gui.opponent_bet,
                is_dealer=self.gui.simulator.Dealer == 0
            )
            self.gui.update_ai_suggestions()  # Update AI suggestions
        else:
            # Random strategy
            bet_amount = amount
            
        # Check if bet is valid
        if bet_amount < self.gui.current_bet:
            self.gui.result_label.config(text="You cannot bet less than the current bet.", fg="red")
            self.gui.log_action("Attempted to bet less than the current bet.")
            return

        # Process the bet
        min_bet = max(self.gui.opponent_bet - self.gui.player_bet, 1)
        bet_amount = max(bet_amount, min_bet)
        if bet_amount > self.gui.player_coins:
            self.fold()
            return

        self.gui.player_bet += bet_amount
        self.gui.player_coins -= bet_amount
        self.gui.current_bet = max(self.gui.player_bet, self.gui.opponent_bet)
        self.gui.update_coins()
        self.gui.update_current_bet_label()
        self.gui.result_label.config(text=f"You bet {bet_amount}.", fg="green")
        self.gui.log_action(f"You bet {bet_amount} coins.")
        self.gui.check_game_over()

        if self.gui.player_bet > 0 and self.gui.opponent_bet > 0:
            if self.gui.simulator.Dealer != 0:
                self.gui.showdown()
        else:
            if self.gui.simulator.Dealer == 0:
                self.gui.root.after(500, self.gui.opponent_handler.act)

class OpponentAction:
    def __init__(self, gui):
        self.gui = gui

    def act(self):
        self.bet()

    def fold(self):
        self.gui.log_action("Opponent folded.")
        self.gui.result_label.config(text="Opponent folded. You take the pot.", fg="green")
        total_pot = self.gui.player_bet + self.gui.opponent_bet
        self.gui.player_coins += total_pot
        self.gui.player_bet = 0
        self.gui.opponent_bet = 0
        self.gui.update_coins()
        self.gui.check_game_over()
        
        self.gui.simulator.Dealer = 1 - self.gui.simulator.Dealer
        self.gui.log_action(f"Dealer switched to {'You' if self.gui.simulator.Dealer == 0 else 'Opponent'}.")

        self.gui.reset_game_with_delay()
        self.gui.disable_player_actions()

    def bet(self):
        # Random strategy for opponent
        action = random.choice(["bet1", "bet2", "fold"])
        
        if action == "fold":
            self.fold()
            return
            
        bet_amount = 1 if action == "bet1" else 2
        min_bet = max(self.gui.player_bet - self.gui.opponent_bet, 1)
        bet_amount = max(bet_amount, min_bet)
        
        if bet_amount > self.gui.opponent_coins:
            self.fold()
            return
            
        self.gui.opponent_bet += bet_amount
        self.gui.opponent_coins -= bet_amount
        self.gui.current_bet = max(self.gui.player_bet, self.gui.opponent_bet)
        self.gui.update_coins()
        self.gui.update_current_bet_label()
        self.gui.result_label.config(text=f"Opponent bets {bet_amount}.", fg="blue")
        self.gui.log_action(f"Opponent bets {bet_amount} coins.")
        self.gui.check_game_over()
        
        if self.gui.player_bet > 0 and self.gui.opponent_bet > 0:
            self.gui.showdown()
        elif self.gui.player_bet == 0 and self.gui.opponent_bet == 0:
            self.gui.showdown()
        else:
            if self.gui.player_handler.strategy == "random":
                self.gui.root.after(500, self.gui.player_handler.act)
            else:
                self.gui.enable_player_actions()
class SimulationStart:
    def __init__(self, gui):
        self.gui = gui

    def start_new_round(self):
        if self.gui.round_number > 1:
            self.gui.log_action("")
        self.gui.log_action(f"Round {self.gui.round_number}")    
        self.gui.round_number += 1  

        self.gui.player_hand, self.gui.opponent_hand = self.gui.simulator.deal_hands()
        self.gui.display_hand(self.gui.player_frame, self.gui.player_hand)
        card_back_path = "./card_back.jpg"
        self.gui.display_hand(self.gui.opponent_frame, [card_back_path] * len(self.gui.opponent_hand))
        dealer_text = "You are the dealer." if self.gui.simulator.Dealer == 0 else "Opponent is the dealer."
        self.gui.dealer_label.config(text=dealer_text)
        self.gui.result_label.config(text="Game started! Make your move.", fg="green")
        self.gui.player_bet = 0
        self.gui.opponent_bet = 0
        self.gui.current_bet = 0
        self.gui.update_current_bet_label()
        self.gui.update_ai_suggestions()

        # 根据庄家决定谁先行动
        if self.gui.simulator.Dealer == 0:
            # 玩家是庄家
            if self.gui.player_handler.strategy == "random":
                # 如果玩家使用random策略，自动执行行动
                self.gui.player_handler.act()
            else:
                # 如果是human策略，启用行动按钮
                self.gui.enable_player_actions()
        else:
            # 对手是庄家，先让对手行动
            self.gui.opponent_handler.act()

        # **移除庄家标志切换**
        # self.gui.simulator.Dealer = 1 - self.gui.simulator.Dealer

class ZhaJinHuaSimulator:
    def __init__(self):
        self.Dealer = random.randint(0, 1)
        self.deck_path = "./PNG-cards-1.3/"
        self.deck = self.get_deck()
        self.player_hand = []
        self.opponent_hand = []

    def get_deck(self):
        if os.path.exists(self.deck_path) and os.path.isdir(self.deck_path):
            deck = os.listdir(self.deck_path)
            deck = [os.path.join(self.deck_path, card) for card in deck if card.endswith(".png")]
            return deck
        return []

    def deal_hands(self, hand_num=3):
        self.deck = self.get_deck()
        if len(self.deck) < hand_num * 2:
            messagebox.showerror("Error", "Not enough cards to deal.")
            return [], []
        if self.Dealer == 0:
            self.player_hand = random.sample(self.deck, hand_num)
            for card in self.player_hand:
                self.deck.remove(card)
            self.opponent_hand = random.sample(self.deck, hand_num)
            for card in self.opponent_hand:
                self.deck.remove(card)
        else:
            self.opponent_hand = random.sample(self.deck, hand_num)
            for card in self.opponent_hand:
                self.deck.remove(card)
            self.player_hand = random.sample(self.deck, hand_num)
            for card in self.player_hand:
                self.deck.remove(card)
        return self.player_hand, self.opponent_hand

class ZhaJinHuaGUI:
    def __init__(self, root, simulator, player_strategy="human"):
        self.round_number = 1
        self.root = root
        self.simulator = simulator
        self.root.geometry("1200x700")
        self.root.title("Zha Jin Hua Game")
        self.player_coins = 5
        self.opponent_coins = 5
        self.current_bet = 0
        self.player_bet = 0
        self.opponent_bet = 0
        self.player_hand = []
        self.opponent_hand = []
        self.player_strategy = player_strategy

        # Initialize AI advisor
        self.score_calculator = ZhaJinHuaScoreCalculator()
        self.ai_advisor = ZhaJinHuaAI(self.score_calculator)

        # 初始化处理器
        self.player_handler = PlayerAction(self, strategy=player_strategy)
        self.opponent_handler = OpponentAction(self)
        self.simulation_handler = SimulationStart(self)

        self.setup_ui()

        # 根据策略禁用或启用按钮
        if self.player_strategy == "human":
            self.disable_player_actions()  # 开始时禁用，等待新回合
        else:
            self.disable_player_actions()  # random策略时禁用按钮

        self.start_game()

    def setup_ui(self):
        # 配置根网格
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)  # 中心区域权重更高
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)

        # 左侧框架
        self.left_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        self.opponent_coins_label = tk.Label(self.left_frame, text=f"Opponent Coins: {self.opponent_coins}", font=("Arial", 16))
        self.opponent_coins_label.pack(pady=20)
        self.current_bet_label = tk.Label(self.left_frame, text=f"Current Bet: {self.current_bet}", font=("Arial", 16))
        self.current_bet_label.pack(pady=20)
        self.player_coins_label = tk.Label(self.left_frame, text=f"Your Coins: {self.player_coins}", font=("Arial", 16))
        self.player_coins_label.pack(pady=20)

        # 中间框架
        self.center_frame = tk.Frame(self.root, bg="#ffffff", padx=10, pady=10)
        self.center_frame.grid(row=0, column=1, sticky="nsew")

        self.title_label = tk.Label(self.center_frame, text="Zha Jin Hua Game", font=("Arial", 24, "bold"), fg="#333333")
        self.title_label.pack(pady=10)

        self.dealer_label = tk.Label(self.center_frame, text="", font=("Arial", 16), fg="blue")
        self.dealer_label.pack(pady=5)

        self.opponent_frame = tk.Frame(self.center_frame, bg="#ffffff")
        self.opponent_frame.pack(pady=10)

        self.player_frame = tk.Frame(self.center_frame, bg="#ffffff")
        self.player_frame.pack(pady=10)

        self.action_frame = tk.Frame(self.center_frame, bg="#ffffff")
        self.action_frame.pack(pady=20)

        self.result_label = tk.Label(self.center_frame, text="", font=("Arial", 16), fg="green")
        self.result_label.pack(pady=10)

        # 动作按钮
        self.bet_button = tk.Button(self.action_frame, text="Bet 1", font=("Arial", 14), 
                                    command=lambda: self.player_handler.bet(1))
        self.bet_button.grid(row=0, column=0, padx=5, pady=5)

        self.bet2_button = tk.Button(self.action_frame, text="Bet 2", font=("Arial", 14), 
                                     command=lambda: self.player_handler.bet(2))
        self.bet2_button.grid(row=0, column=1, padx=5, pady=5)

        self.fold_button = tk.Button(self.action_frame, text="Fold", font=("Arial", 14), 
                                     command=self.player_handler.fold)
        self.fold_button.grid(row=0, column=2, padx=5, pady=5)

        # 移除 Check 按钮
        # self.check_button = tk.Button(self.action_frame, text="Check", font=("Arial", 14), 
        #                               command=self.player_handler.showdown)
        # self.check_button.grid(row=0, column=3, padx=5, pady=5)

        # 右侧框架
        self.right_container = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        self.right_container.grid(row=0, column=2, sticky="nsew")

        # 游戏日志
        self.right_frame_log = tk.Frame(self.right_container, bg="#f0f0f0")
        self.right_frame_log.pack(fill="both", expand=True, pady=10)
        self.log_label = tk.Label(self.right_frame_log, text="Game Log", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.log_label.pack(pady=5)
        self.log_text = tk.Text(self.right_frame_log, width=30, height=20, state="disabled", bg="#e6e6e6")
        self.log_text.pack(pady=5, padx=5, fill="both", expand=True)

        # AI建议（可选）
        self.right_frame_ai = tk.Frame(self.right_container, bg="#f0f0f0")
        self.right_frame_ai.pack(fill="both", expand=True, pady=10)
        self.ai_label = tk.Label(self.right_frame_ai, text="AI Suggestions", font=("Arial", 14, "bold"), bg="#f0f0f0")
        self.ai_label.pack(pady=5)
        self.ai_text = tk.Text(self.right_frame_ai, width=30, height=15, state="disabled", bg="#e6e6e6")
        self.ai_text.pack(pady=5, padx=5, fill="both", expand=True)

    def start_game(self):
        self.simulation_handler.start_new_round()
        # 动作由SimulationStart.start_new_round()根据庄家决定

    def display_hand(self, frame, hand):
        for widget in frame.winfo_children():
            widget.destroy()
        for card_path in hand:
            if os.path.exists(card_path):
                img = Image.open(card_path).resize((80, 120))
            else:
                # 如果卡片图片不存在，使用占位图
                img = Image.new('RGB', (80, 120), color='gray')
            card_img = ImageTk.PhotoImage(img)
            card_label = tk.Label(frame, image=card_img)
            card_label.image = card_img
            card_label.pack(side="left", padx=5)

    def log_action(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def calculate_score(self, hand):
        """
        Calculate score for Zha Jin Hua (Chinese Poker) hands
        Returns tuple (hand_type_rank, high_card_value) where hand_type_rank is:
        7 - Three of a kind (豹子)
        6 - Straight Flush (同花顺)
        5 - Flush (同花)
        4 - Straight (顺子)
        3 - Pair (对子)
        2 - High Card (单张)
        """
        # Parse cards from filenames like "2_of_hearts.png"
        cards = []
        for card in hand:
            filename = os.path.basename(card)
            # Split the filename to get rank and suit
            # Example: "2_of_hearts.png" -> ["2", "of", "hearts.png"]
            parts = filename.split('_')
            rank = parts[0]
            suit = parts[2].split('.')[0]  # Remove ".png" extension
            
            # Convert rank to numeric value
            rank_value = {
                'ace': 14, 'king': 13, 'queen': 12, 'jack': 11,
                '10': 10, '9': 9, '8': 8, '7': 7,
                '6': 6, '5': 5, '4': 4, '3': 3, '2': 2
            }.get(rank.lower(), int(rank) if rank.isdigit() else 0)
            
            cards.append((rank_value, suit))
        
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
            straight_value = 3  # In A-2-3 straight, 3 is the highest card
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
            # Find the pair value
            for value in values:
                if values.count(value) == 2:
                    return 3, value
        
        # High Card (单张)
        return 2, max(values)

    def update_coins(self):
        self.player_coins_label.config(text=f"Your Coins: {self.player_coins}")
        self.opponent_coins_label.config(text=f"Opponent Coins: {self.opponent_coins}")

    def update_current_bet_label(self):
        total_bet = self.player_bet + self.opponent_bet
        self.current_bet_label.config(text=f"Current Bet: {total_bet}")

    def reset_game_with_delay(self):
        self.root.after(2000, self.simulation_handler.start_new_round)

    def check_game_over(self):
        if self.player_coins <= 0:
            messagebox.showinfo("Game Over", "You lose! Opponent wins the game.")
            self.root.quit()
        elif self.opponent_coins <= 0:
            messagebox.showinfo("Game Over", "You win! Opponent is out of coins.")
            self.root.quit()

    # 方法来启用和禁用玩家行动按钮
    def enable_player_actions(self):
        if self.player_strategy == "human":
            self.bet_button.config(state="normal")
            self.bet2_button.config(state="normal")
            self.fold_button.config(state="normal")
            # self.check_button.config(state="normal")  # 已移除 Check 按钮

    def disable_player_actions(self):
        self.bet_button.config(state="disabled")
        self.bet2_button.config(state="disabled")
        self.fold_button.config(state="disabled")
        # self.check_button.config(state="disabled")  # 已移除 Check 按钮

    def showdown(self):
        # Disable player actions as the round is ending
        self.disable_player_actions()

        if self.player_bet == 0 and self.opponent_bet == 0:
            self.result_label.config(text="Both players checked. It's a draw!", fg="orange")
            self.log_action("Both players checked. Bets are returned.")
            self.update_ai_suggestions("It's a draw! Consider your next move.")
            self.simulator.Dealer = 1 - self.simulator.Dealer
            self.log_action(f"Dealer switched to {'Opponent' if self.simulator.Dealer == 1 else 'You'}.")
            self.reset_game_with_delay()
            return

        total_pot = self.player_bet + self.opponent_bet
        self.log_action(f"Total pot is {total_pot} coins.")
        self.display_hand(self.opponent_frame, self.opponent_hand)  # Show opponent's cards
        
        player_result = self.calculate_score(self.player_hand)
        opponent_result = self.calculate_score(self.opponent_hand)
        
        # Log the hands for debugging
        hand_types = {
            7: "Three of a Kind",
            6: "Straight Flush",
            5: "Flush",
            4: "Straight",
            3: "Pair",
            2: "High Card"
        }
        self.log_action(f"Your hand: {hand_types[player_result[0]]} (High card: {player_result[1]})")
        self.log_action(f"Opponent's hand: {hand_types[opponent_result[0]]} (High card: {opponent_result[1]})")

        # Compare hands - first by type, then by value if types are equal
        if player_result[0] > opponent_result[0] or \
        (player_result[0] == opponent_result[0] and player_result[1] > opponent_result[1]):
            self.player_coins += total_pot
            self.result_label.config(text=f"You win! 🎉 You take {total_pot} coins.", fg="green")
            self.log_action(f"You won {total_pot} coins in the showdown.")
            self.update_ai_suggestions("Great job! You have a stronger hand.")
        elif player_result[0] < opponent_result[0] or \
            (player_result[0] == opponent_result[0] and player_result[1] < opponent_result[1]):
            self.opponent_coins += total_pot
            self.result_label.config(text=f"You lose! 😢 Opponent takes {total_pot} coins.", fg="red")
            self.log_action(f"Opponent won {total_pot} coins in the showdown.")
            self.update_ai_suggestions("Opponent has a stronger hand. Try to improve your strategy.")
        else:
            # True tie - split the pot
            self.player_coins += self.player_bet
            self.opponent_coins += self.opponent_bet
            self.result_label.config(text="It's a draw! 🤝", fg="orange")
            self.log_action("It's a draw! Bets are returned.")
            self.update_ai_suggestions("It's a draw. Both players retain their bets.")

        # Reset bets
        self.player_bet = 0
        self.opponent_bet = 0

        # Switch dealer
        self.simulator.Dealer = 1 - self.simulator.Dealer
        self.log_action(f"Dealer switched to {'Opponent' if self.simulator.Dealer == 1 else 'You'}.")

        self.update_coins()
        self.check_game_over()
        self.reset_game_with_delay()
        
    def update_ai_suggestions(self, suggestion=None):
        if suggestion:
            ai_message = suggestion
        else:
            current_state = ZhaJinHuaState(
                player_hand=self.player_hand,
                player_coins=self.player_coins,
                opponent_coins=self.opponent_coins,
                player_bet=self.player_bet,
                opponent_bet=self.opponent_bet,
                is_dealer=self.simulator.Dealer == 0
            )
            ai_message = self.ai_advisor.get_suggestion(current_state)
            
        self.ai_text.config(state="normal")
        self.ai_text.delete(1.0, tk.END)
        self.ai_text.insert(tk.END, ai_message)
        self.ai_text.config(state="disabled")

if __name__ == "__main__":
    simulator = ZhaJinHuaSimulator()
    root = tk.Tk()
    player_strategy = "human"  # Change to "human" for manual play
    app = ZhaJinHuaGUI(root, simulator, player_strategy=player_strategy)
    root.mainloop()
