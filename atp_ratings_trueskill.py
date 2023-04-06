# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import pickle

from trueskillthroughtime import History, Player, Gaussian
from utils import load_atp_data


def main():

    # loading the atp data
    print("loading the atp data")
    df = load_atp_data()
    # figuring out how to do it set by set instead of match by match
    # requires dropping nans from score and excluding >3 set matches

    df.dropna(subset='score', inplace=True)

    df['match_length'] = [len(x.split(' ')) for x in df.score]
    df = df[df['match_length'] <= 3].copy()

    list_for_df = []

    for x, y, z in zip(df.winner_name, df.loser_name, df.match_length):

        if z == 2:
            list_for_df.append([x, y])
            list_for_df.append([x, y])
        else:
            list_for_df.append([x, y])
            list_for_df.append([y, x])
            list_for_df.append([x, y])

    # creating the trueskill dictionary
    print("preparing the true skill model")
    columns = zip(df.winner_name, df.loser_name, df.surface)

    composition = [[[winner, winner + surface], [loser, loser + surface]]
                   for winner, loser, surface in columns]

    all_atp_players = set([val for sublist in zip(
        df.winner_name, df.loser_name) for val in sublist])

    # defining the prior ratings. values are from the optimization
    # noetbook
    priors = dict([(p, Player(Gaussian(0., 1.51), 1.5, 0.098))
                  for p in all_atp_players])

    # doing a first pass with TrueSkill. params from the optimization
    # notebook
    true_skill_history_priors = History(composition=composition,
                                        priors=priors,
                                        beta=0,
                                        sigma=0.5,
                                        gamma=0.01)

    # running the TrueSkillThroughTime algorithm
    print("running the ttt algorithm. please wait 10-15 minutes.")
    true_skill_history_priors.convergence(epsilon=0.01, iterations=10)

    # creating the dictionaries of player names and ratings
    # the big dict contains the entire skill history of each player
    mens_big_dict = true_skill_history_priors.learning_curves()

    # the small dict contains only the most recent skill rating
    mens_small_dict = dict()

    for key in mens_big_dict.keys():
        if key not in mens_small_dict:
            mens_small_dict[key] = mens_big_dict[key][-1]
            
    return mens_big_dict, mens_small_dict, all_atp_players

if __name__ == '__main__':
    a, b, c = main()

    # saving the files needed using pickle
    print("saving the atp ratings to the final_ratings folder")
    with open('final_ratings/mens_big_dict.pickle', 'wb') as handle:
        pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)
        
    with open('final_ratings/mens_small_dict.pickle', 'wb') as handle2:
        pickle.dump(b, handle2, protocol=pickle.HIGHEST_PROTOCOL)
        
    with open('final_ratings/mens_names.pickle', 'wb') as file:
        pickle.dump(c, file, protocol=pickle.HIGHEST_PROTOCOL)