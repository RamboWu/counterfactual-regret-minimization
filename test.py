# Kuhn Poker Def
import random

PASS = 0
BET = 1
NUM_ACTIONS = 2
node_map = dict()  # str -> Node


class Node:
    def __init__(self):
        self.info_set = ''
        self.regret_sum = [0 for i in range(NUM_ACTIONS)]
        self.strategy = [0 for i in range(NUM_ACTIONS)]
        self.strategy_sum = [0 for i in range(NUM_ACTIONS)]

    # Get current information set mixed strategy through regret-matching
    def get_strategy(self, realization_weight):
        norm_sum = 0
        for a in range(NUM_ACTIONS):
            self.strategy[a] = max(self.regret_sum[a], 0)
            norm_sum += self.strategy[a]
        for a in range(NUM_ACTIONS):
            if norm_sum > 0:
                self.strategy[a] /= norm_sum
            else:
                self.strategy[a] = 1 / NUM_ACTIONS
            self.strategy_sum[a] += realization_weight * self.strategy[a]
        return self.strategy

    # Get average information set mixed strategy across all training iterations
    def get_avg_strategy(self):
        avg_strategy = [0 for i in range(NUM_ACTIONS)]
        norm_sum = 0
        for a in range(NUM_ACTIONS):
            norm_sum += self.strategy_sum[a]
        for a in range(NUM_ACTIONS):
            if norm_sum > 0:
                avg_strategy[a] = self.strategy_sum[a] / norm_sum
            else:
                avg_strategy[a] = 1 / NUM_ACTIONS
        return avg_strategy

    def __str__(self):
        return str(self.info_set) + str(self.get_avg_strategy())


def cfr(cards, history, p0, p1):
    #print( history, p0, p1)
    plays = len(history)
    player = plays % 2
    opponent = 1 - player
    # terminal case
    if plays > 1:
        terminal_pass = history[plays - 1] == 'p'
        double_bet = history[-2:] == 'bb'
        play_higher = cards[player] > cards[opponent]
        if terminal_pass:
            if history == 'bb' and not play_higher:
                return -1
            else:
                return 1
        elif double_bet:
            return 2 if play_higher else -2
    info_set = str(cards[player]) + history
    # get information set node or create it if doesn't exist
    if info_set not in node_map:
        node = Node()
        node.info_set = info_set
        node_map[info_set] = node
    node = node_map[info_set]
    # for each action,recursively call cfr with history and prob
    strategy = node.get_strategy(p0 if player == 0 else p1)
    util = [0 for i in range(NUM_ACTIONS)]
    node_util = 0
    for a in range(NUM_ACTIONS):
        next_history = history + ('p' if a == 0 else 'b')
        util[a] = -cfr(cards, next_history, p0 * strategy[a], p1) \
            if player == 0 else \
            -cfr(cards, next_history, p0, p1 * strategy[a])
        node_util += strategy[a] * util[a]
    for a in range(NUM_ACTIONS):
        regret = util[a] - node_util  # your util is your opponents' regret
        node.regret_sum[a] += (p1 if player == 0 else p0) * regret
    return node_util


def train(iterations):
    cards = [2, 1, 3]
    util = 0
    for i in range(iterations):
        random.shuffle(cards)
        util += cfr(cards, '', 1, 1)
    print(f"avg game value:{util / iterations}")
    # for n in range(node_map):
    #     print(n)


if __name__ == '__main__':
    iterations = 2000
    train(iterations)
    for n in node_map:
        print(n, str(node_map[n]))
        print(node_map[n].regret_sum)
        print(node_map[n].strategy)
        print('--------')

# 2 2[0.9999811597186752, 1.88402813248449e-05]
# 3p 3p[1.4982754849168608e-06, 0.9999985017245151]
# 2pb 2pb[0.6648570928739191, 0.33514290712608075]
# 3b 3b[1.4982754849168608e-06, 0.9999985017245151]
# 1p 1p[0.6679740612234988, 0.3320259387765012]
# 1b 1b[0.9999954971181556, 4.502881844380404e-06]
# 1 1[0.9999985006821897, 1.4993178103962698e-06]
# 2p 2p[1.5007668918817515e-06, 0.9999984992331081]
# 1pb 1pb[0.9999992503399708, 7.496600291767683e-07]
# 2b 2b[0.5435192682908098, 0.4564807317091902]
# 3 3[0.9999899130831076, 1.00869168924377e-05]
# 3pb 3pb[7.518737158266613e-07, 0.9999992481262842]
