# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:20:08 2023

@author: yaobv
"""

import pickle

from trueskillthroughtime import History, Player, Gaussian
from utils import load_wta_data

df = load_wta_data()

# creating the trueskill dict for the wta players

columns = zip(df.winner_name, df.loser_name, df.surface)

composition = [[[winner, winner + surface], [loser, loser + surface]]
               for winner, loser, surface in columns]

all_wta_players = set([val for sublist in zip(
    df.winner_name, df.loser_name) for val in sublist])

priors = dict([(p, Player(Gaussian(0., 1.51), 1.5, 0.098))
              for p in all_wta_players])

true_skill_history_priors = History(composition=composition,
                                    priors=priors,
                                    beta=0,
                                    sigma=0.5,
                                    gamma=0.01)

# running the TTT dict

true_skill_history_priors.convergence(epsilon=0.01, iterations=10)

womens_big_dict = true_skill_history_priors.learning_curves()

womens_small_dict = dict()

for key in womens_big_dict.keys():
    if key not in womens_small_dict:
        womens_small_dict[key] = womens_big_dict[key][-1]


with open('women_names.pickle', 'wb') as names:
    pickle.dump(all_wta_players, names, protocol=pickle.HIGHEST_PROTOCOL)


with open('womens_big_dict.pickle', 'wb') as file:
    pickle.dump(womens_big_dict, file, protocol=pickle.HIGHEST_PROTOCOL)
    
    
with open('womens_small_dict.pickle', 'wb') as file_b:
    pickle.dump(womens_small_dict, file_b, protocol=pickle.HIGHEST_PROTOCOL)