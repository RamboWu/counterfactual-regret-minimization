from common.constants import CARDS_DEALINGS
from games.kuhn import KuhnRootChanceGameState
from games.algorithms import ChanceSamplingCFR, VanillaCFR
import json


root = KuhnRootChanceGameState(CARDS_DEALINGS)
chance_sampling_cfr = ChanceSamplingCFR(root)
chance_sampling_cfr.run(iterations = 10000)
chance_sampling_cfr.compute_nash_equilibrium()
#chance_sampling_cfr.value_of_the_game()

data2 = json.dumps(chance_sampling_cfr.nash_equilibrium, sort_keys=True, indent=4, separators=(',', ': '))
print(data2)

#现在看 regrets值，就是 负的 看起来正常，但是 正的 regrets很小
#data2 = json.dumps(chance_sampling_cfr.cumulative_regrets, sort_keys=True, indent=4, separators=(',', ': '))
#print(data2)

#print('--------')
#chance_sampling_cfr.run(iterations = 1)

#data2 = json.dumps(chance_sampling_cfr.cumulative_regrets, sort_keys=True, indent=4, separators=(',', ': '))
#print(data2)
#print(chance_sampling_cfr.sigma)
# read Nash-Equilibrum via chance_sampling_cfr.nash_equilibrium member
# try chance_sampling_cfr.value_of_the_game() function to get value of the game (-1/18)

# vanilla cfr
#vanilla_cfr = VanillaCFR(root)
#vanilla_cfr.run(iterations = 1000)
#vanilla_cfr.compute_nash_equilibrium()
