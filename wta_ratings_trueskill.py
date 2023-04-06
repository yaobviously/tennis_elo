# -*- coding: utf-8 -*-
"""
Created on Sun Jan 22 15:20:08 2023

@author: yaobv
"""

import pickle

from trueskillthroughtime import History, Player, Gaussian
from utils import load_wta_data


def main():

    # loading the wta data
    print("loading the wta data")
    df = load_wta_data()

    # creating the trueskill dict for the wta players
    print("preparing the wta data for the true skill algorithm")
    columns = zip(df.winner_name, df.loser_name, df.surface)

    composition = [[[winner, winner + surface], [loser, loser + surface]]
                   for winner, loser, surface in columns]

    all_wta_players = set([val for sublist in zip(
        df.winner_name, df.loser_name) for val in sublist])

    # defining the priors for the WTA trueskill model
    priors = dict([(p, Player(Gaussian(0., 1.51), 1.5, 0.098))
                  for p in all_wta_players])

    true_skill_history_priors = History(composition=composition,
                                        priors=priors,
                                        beta=0,
                                        sigma=0.5,
                                        gamma=0.01)

    # running the TTT algorithm
    print("running ttt. will take 10min")
    true_skill_history_priors.convergence(epsilon=0.01, iterations=10)
    
    # creating the dictionaries of true skill ratings
    womens_big_dict = true_skill_history_priors.learning_curves()
    womens_small_dict = dict()

    for key in womens_big_dict.keys():
        if key not in womens_small_dict:
            womens_small_dict[key] = womens_big_dict[key][-1]

    return womens_big_dict, womens_small_dict, all_wta_players


if __name__ == '__main__':
    a, b, c = main()
    
    print("saving the filds to final_ratings folder")
    with open('final_ratings/womens_big_dict.pickle', 'wb') as file:
        pickle.dump(a, file, protocol=pickle.HIGHEST_PROTOCOL)

    with open('final_ratings/womens_small_dict.pickle', 'wb') as file_b:
        pickle.dump(b, file_b, protocol=pickle.HIGHEST_PROTOCOL)

    with open('final_ratings/womens_names.pickle', 'wb') as names:
        pickle.dump(c, names, protocol=pickle.HIGHEST_PROTOCOL)