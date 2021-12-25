from common.constants import A, QK, QJ
from common.utils import init_sigma, init_empty_node_maps

class CounterfactualRegretMinimizationBase:

    def __init__(self, root, chance_sampling = False):
        self.root = root
        self.sigma = init_sigma(root)
        self.cumulative_regrets = init_empty_node_maps(root)
        self.chance_sampling = chance_sampling

    def print_sigma(self):
        #print('when k comes:', self.sigma['.K.'])
        for info in self.sigma:
            for action in self.sigma[info]:
                print(info, ' |A:', action, ' |S:', self.sigma[info][action])

    def print_sigma_and_regrets(self):
        for info in self.sigma:
            for action in self.sigma[info]:
                print(info, ' |A:', action,
                ' |S:', self.sigma[info][action] ,
                ' |R:', self.cumulative_regrets[info][action])

    def _update_sigma(self, i):
        rgrt_sum = sum(filter(lambda x : x > 0, self.cumulative_regrets[i].values()))
        for a in self.cumulative_regrets[i]:
            self.sigma[i][a] = max(self.cumulative_regrets[i][a], 0.) / rgrt_sum if rgrt_sum > 0 else 1. / len(self.cumulative_regrets[i].keys())

    def _cumulate_cfr_regret(self, information_set, action, regret):
        self.cumulative_regrets[information_set][action] += regret

    def run(self, iterations):
        raise NotImplementedError("Please implement run method")

    def _cfr_utility_recursive(self, state, reach_a, reach_b, need_print = False):
        children_states_utilities = {}
        if state.is_terminal():
            # evaluate terminal node according to the game result
            return state.evaluation()
        if state.is_chance():
            if self.chance_sampling:
                # if node is a chance node, lets sample one child node and proceed normally
                return self._cfr_utility_recursive(state.sample_one(), reach_a, reach_b)
            else:
                chance_outcomes = {state.play(action) for action in state.actions}
                return state.chance_prob() * sum([self._cfr_utility_recursive(outcome, reach_a, reach_b) for outcome in chance_outcomes])
        # sum up all utilities for playing actions in our game state
        value = 0.
        for action in state.actions:
            child_reach_a = reach_a * (self.sigma[state.inf_set()][action] if state.to_move == A else 1)
            child_reach_b = reach_b * (self.sigma[state.inf_set()][action] if state.to_move == -A else 1)
            # value as if child state implied by chosen action was a game tree root
            child_state_utility = self._cfr_utility_recursive(state.play(action), child_reach_a, child_reach_b, need_print)
            # value computation for current node
            value +=  self.sigma[state.inf_set()][action] * child_state_utility
            # values for chosen actions (child nodes) are kept here
            children_states_utilities[action] = child_state_utility
        # we are computing regrets for both players simultaneously, therefore we need to relate reach,reach_opponent to the player acting
        # in current node, for player A, it is different than for player B
        (cfr_reach, reach) = (reach_b, reach_a) if state.to_move == A else (reach_a, reach_b)
        for action in state.actions:
            # we multiply regret by -1 for player B, this is because value is computed from player A perspective
            # again we need that perspective switch
            action_cfr_regret = state.to_move * cfr_reach * (children_states_utilities[action] - value)
            if action_cfr_regret <= 0:
                action_cfr_regret = 0
            if need_print:
                print('----------------------')
                print(state.inf_set(), '|A:', action, '|G:', action_cfr_regret)
                print('To_move:', state.to_move, 'payoff: ', children_states_utilities[action], ' value:', value)
            self._cumulate_cfr_regret(state.inf_set(), action, action_cfr_regret)
        if self.chance_sampling:
            # update sigma according to cumulative regrets - we can do it here because we are using chance sampling
            # and so we only visit single game_state from an information set (chance is sampled once)
            self._update_sigma(state.inf_set())
        return value

class VanillaCFR(CounterfactualRegretMinimizationBase):

    def __init__(self, root):
        super().__init__(root = root, chance_sampling = False)

    def run(self, iterations = 1):
        for _ in range(0, iterations):
            self._cfr_utility_recursive(self.root, 1, 1)
            # since we do not update sigmas in each information set while traversing, we need to
            # traverse the tree to perform to update it now
            self.__update_sigma_recursively(self.root)

    def __update_sigma_recursively(self, node):
        # stop traversal at terminal node
        if node.is_terminal():
            return
        # omit chance
        if not node.is_chance():
            self._update_sigma(node.inf_set())
        # go to subtrees
        for k in node.children:
            self.__update_sigma_recursively(node.children[k])

class ChanceSamplingCFR(CounterfactualRegretMinimizationBase):

    def __init__(self, root):
        super().__init__(root = root, chance_sampling = True)

    def run(self, iterations = 1):
        for _ in range(0, iterations):
            self._cfr_utility_recursive(self.root, 1, 1)

    def test_run(self):
        for _ in range(0, 1000):
            self._cfr_utility_recursive(self.root, 1, 1)
        self.print_sigma()
        print('--------------Try QK--------------')
        self._cfr_utility_recursive(self.root.children[QK], 1, 1, True)
