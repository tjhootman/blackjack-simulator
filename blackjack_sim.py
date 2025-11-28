import random
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D  # Required for the custom legend

# --- CONFIGURATION (The Control Panel) ---
STARTING_BANKROLL = 2000    # Starting cash
BET_SIZE = 25               # Flat bet per hand
TOTAL_HANDS = 1000          # Hands played per session
SIMULATIONS = 100           # Number of players to simulate

# RULE SETTINGS
IS_6_TO_5 = False           # True = "Carnival" rules (1.2x payout) - House Edge ~2%
                            # False = Standard rules (1.5x payout) - House Edge ~0.5%

def play_hand_pro(current_bankroll, bet, is_6to5):
    """
    Simulates a single hand using weighted probabilities based on 
    Perfect Basic Strategy in a 6-Deck S17 game.
    """
    # 1. Determine Blackjack Payout
    bj_payout = 1.2 if is_6to5 else 1.5

    # 2. Define Outcomes & Probabilities
    # These weights represent the frequency of final bankroll impacts.
    # We use the CORRECTED weights here so the House Edge is realistic (~0.5%).
    outcomes = [
        "Blackjack",      # Pays 3:2 or 6:5
        "Standard Win",   # Pays 1:1
        "Double Win",     # Pays 2:1 (Successful Double Down or Split)
        "Push",           # Pays 0
        "Standard Loss",  # Lose 1 unit
        "Double Loss"     # Lose 2 units (Failed Double Down or Split)
    ]
    
    # Probabilities (Sum ~= 1.0)
    weights = [
        0.048,  # Blackjack (~4.8%)
        0.358,  # Standard Win (~35.8%)
        0.040,  # Double/Split Win (~4.0%)
        0.085,  # Push (~8.5%)
        0.427,  # Standard Loss (~42.7%) <--- The most common outcome
        0.042   # Double/Split Loss (~4.2%)
    ]
    
    # 3. Select Random Result
    result = random.choices(outcomes, weights=weights, k=1)[0]

    # 4. Calculate Bankroll Change
    if result == "Blackjack":
        return current_bankroll + (bet * bj_payout)
    elif result == "Standard Win":
        return current_bankroll + bet
    elif result == "Double Win":
        return current_bankroll + (bet * 2)
    elif result == "Push":
        return current_bankroll
    elif result == "Standard Loss":
        return current_bankroll - bet
    elif result == "Double Loss":
        return current_bankroll - (bet * 2)
    
    return current_bankroll

def run_simulation():
    """Run one player's session"""
    bankroll = STARTING_BANKROLL
    history = [bankroll]
    
    for _ in range(TOTAL_HANDS):
        # Stop if broke (Ruin)
        if bankroll < BET_SIZE:
            history.append(0) 
            break
            
        bankroll = play_hand_pro(bankroll, BET_SIZE, IS_6_TO_5)
        history.append(bankroll)
        
    return history

# --- EXECUTION ---
print(f"Running {SIMULATIONS} simulations...")
print(f"Rules: {'6:5 (Bad)' if IS_6_TO_5 else '3:2 (Standard)'}")

all_results = []
ruin_count = 0

for i in range(SIMULATIONS):
    path = run_simulation()
    all_results.append(path)
    if path[-1] <= 0:
        ruin_count += 1

# --- ANALYSIS ---
final_values = [r[-1] for r in all_results]
avg_bankroll = sum(final_values) / len(final_values)
ror = (ruin_count / SIMULATIONS) * 100
profit = avg_bankroll - STARTING_BANKROLL

print("-" * 30)
print(f"AVG RESULT: ${avg_bankroll:.2f} ({'+' if profit > 0 else ''}${profit:.2f})")
print(f"RISK OF RUIN: {ror:.1f}%")
print("-" * 30)

# --- VISUALIZATION ---
plt.figure(figsize=(12, 7))
plt.title(f"Bankroll Variance: {SIMULATIONS} Players over {TOTAL_HANDS} Hands")
plt.xlabel("Hands Played")
plt.ylabel("Bankroll ($)")

# Draw Reference Lines
plt.axhline(y=STARTING_BANKROLL, color='black', linestyle='--', linewidth=1)
plt.axhline(y=0, color='red', linestyle='-', linewidth=2)

# Plot the Simulation Lines
for path in all_results:
    # Logic to color lines
    if path[-1] <= 0:
        c = 'red'       # Ruined
        alpha = 0.5
    elif path[-1] > STARTING_BANKROLL:
        c = 'green'     # Profit
        alpha = 0.3
    else:
        c = 'gray'      # Loss but survived
        alpha = 0.3
        
    plt.plot(path, color=c, linewidth=1, alpha=alpha)

# --- CUSTOM LEGEND ---
legend_elements = [
    Line2D([0], [0], color='green', lw=2, label='Profitable'),
    Line2D([0], [0], color='gray', lw=2, label='Loss (Survived)'),
    Line2D([0], [0], color='red', lw=2, label='Ruined ($0)'),
    Line2D([0], [0], color='black', lw=1, linestyle='--', label='Start Amount')
]

plt.legend(handles=legend_elements, loc='upper left')

plt.tight_layout()
plt.show()