import random

# Symbols pool: 7 dominant + 7 others
symbols = ['⚡️'] * 7 + ['🌌', '🔮', '💎', '🪐', '⭐', '🌟', '🚀']

# Define 25 paylines (row indices 0-6)
paylines = [
    [3,3,3,3,3],  # 1 mid
    [2,2,2,2,2],  # 2
    [4,4,4,4,4],  # 3
    [1,1,1,1,1],  # 4
    [5,5,5,5,5],  # 5
    [0,1,2,3,4],  # 6 diagonal down
    [6,5,4,3,2],  # 7 diagonal up
    [2,3,4,3,2],  # 8 V
    [4,3,2,3,4],  # 9 inverted V
    [0,0,0,0,0],  # 10 top
    [6,6,6,6,6],  # 11 bottom
    [1,2,3,4,5],  # 12
    [5,4,3,2,1],  # 13
    [0,1,0,1,0],  # 14 zigzag
    [6,5,6,5,6],  # 15
    [1,0,1,0,1],  # 16
    [5,6,5,6,5],  # 17
    [0,2,4,6,5],  # 18 random wave
    [6,4,2,0,1],  # 19
    [3,2,1,2,3],  # 20 small V
    [3,4,5,4,3],  # 21 small inverted V
    [2,1,0,1,2],  # 22
    [4,5,6,5,4],  # 23
    [1,3,5,3,1],  # 24
    [5,3,1,3,5],  # 25
    [5,4,4,4,5],  #26
    [1,2,2,2,1],  #27
    [7,7,7,7,7],  #28
]

def simulate_spins(num_paylines, num_simulations=1000):
    wins = 0
    for _ in range(num_simulations):
        # Generate grid: 5 reels x 7 rows
        grid = [[random.choice(symbols) for _ in range(7)] for _ in range(5)]
        has_win = False
        for i in range(num_paylines):
            pl = paylines[i]
            line = [grid[j][pl[j]] for j in range(5)]
            if all(s == line[0] for s in line):
                has_win = True
                break  # Count as win if at least one payline wins
        if has_win:
            wins += 1
    win_rate = wins / num_simulations
    odds = round(1 / win_rate) if win_rate > 0 else float('inf')
    print(odds)
    return odds

# Simulate for different payline counts
payline_options = [1, 3, 6, 10, 15, 21, 28]
odds_map = {}
for n in payline_options:
    odds_map[n] = simulate_spins(n)

print(odds_map)
